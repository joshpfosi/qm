# Python library to compute the SOP minimization of a given boolean
# function

__author__ = "Josh Pfosi"

import qm
import sys
import re
from math import *
from sympy import *
from numpy.random import randint
from numpy import unique

debug = False

# on test.txt, javascript implementation chooses 3,19 where I choose 17,19.
# these are the same cost so should be fine but wanted to check

# Args: func - string defining minterms and don't cares
# Returns: dict w/ ones and dc elements
# Notes: This correctly parses desired input but will fail silently on
# poorly formed input
def parse_func(func):
    func = ''.join(func.split()) # remove all whitespace characters

    ones = func
    dcs  = []

    if "+" in func:
        (ones, dcs) = func.split('+')
        dcs  = [int(i) for i in dcs[2:-1].split(',')]

    # remove 'm(' and ')' and cast to integers
    ones = [int(i) for i in ones[2:-1].split(',')]

    return (ones, dcs)

def nice_print(result=[], numVars=0, sop=True):
    print result
    if numVars < 1 or numVars > 10: 
        sys.stderr.write("Cannot handle more than 10 variables or less than 1 variable\n")
        return

    # hard code special case where all minterms are covered
    if len(result) == 1 and len(result[0].replace("X", "")) == 0:
        print "=1"
        return

    variables = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    eq = ''

    for epi in result:
        if not sop: eq += "("

        while epi.endswith("X"): epi = epi[:-1] # leave off trailing dont cares

        if sop:
            for i, lit in enumerate(epi):
                if lit is "X": continue

                eq += variables[i]
                if lit is "0": eq += "'"
            eq += "+" 
        else:
            for i, lit in enumerate(epi):
                if lit is "X": continue

                eq += variables[i] + "+"
                if lit is "1": eq = eq[:-1] + "'+"

            eq = eq[:-1] + ")" # replace last plus with ')'

    if sop: eq = eq[:-1]

    print "=%s" % eq

# Args: low, high - two binary strings such as '0001' and '0010'
# Returns True if they can be legally combined i.e. if dcs match, and minterms 
# within power of two
#         Otherwise, returns None
#
# Note: Always pass "lower" PI as first arg
def combine(low, high):
    lowLen  = len(low)
    highLen = len(high)

    if lowLen != highLen: raise "Cannot combine implicants of different length"

    combo = ''
    diff  = 0
    for i in range(lowLen):
        if low[i] is high[i]: combo += low[i]
        else:
            combo += "X"
            diff  += 1

    if diff > 1: return None # if they differ by more than 1 bit
    else:        return combo

# Args: nCubes - array of string representing n-cubes
# Returns an array of all the prime implicants generated by recursing
# on that list
def generatePis(nCubes):
    size = len(nCubes)

    if size is 0: return []

    nextNCubes = []
    pis        = []
    pis        += nCubes # they all start unmarked

    # iterate over all n-cubes, combining and marking if differing by only 1 bit
    for i in range(size):
        for j in range (i + 1, size):
            combination = combine(nCubes[i], nCubes[j])

            if combination is not None:
                # duplicates don't get added twice
                if combination not in nextNCubes: nextNCubes += [combination]

                # "check" off implicants only once
                if nCubes[i] in pis: pis.remove(nCubes[i])
                if nCubes[j] in pis: pis.remove(nCubes[j])

    return pis + generatePis(nextNCubes)

# Args: pi - converts input of form "-01-" to the minterms that it defines
# Returns list of minerms e.g. [1,2,3,4]
def literalsToMinterms(pi):
    size = len(pi)
    minterms = range(2**size) # all minterms are possible - now eliminate

    # compare each bit of the pi, to the respective bit in each minterm
    for i in range(size): # for each bit in pi
        if pi[i] is "X": continue

        for m in range(2**size): # for each possible minterm
            binary = bin(m)[2:].zfill(size)
            if (m in minterms and binary[i] is not pi[i]): minterms.remove(m)

    return minterms

def mintermsToLiterals(minterms, numVars):
    size = len(minterms)

    # if null list or size isn't a power of two, return
    if size == 0 or (size & (size - 1)) != 0: return ''

    # map minterms to binary e.g. [1,2,3,4] => ['0001','0010','0011','0100']
    binaryMintermLists = [list(bin(m)[2:].zfill(numVars)) for m in minterms]

    # take list of binary values and form array of arrays where the ith subarray
    # contains all the ith bits of all the binary values
    # e.g. ['0001','0010','0011','0100'] => 
    #      [[0,0,0,0],[0,0,0,1],[0,1,1,0],[1,0,1,0]]
    zipped = []
    for i in range(numVars):
        zipElem = []
        for binary in binaryMintermLists:
            zipElem += [binary[i]]

        zipped += [zipElem]


    literal = ''
    for ithBitSet in zipped:
        # if all the same, then just put that value, otherwise its a dc
        if len(set(ithBitSet)) == 1: literal += ithBitSet[0]
        else: literal += "X"

    return literal

# Args: list1 - list to find in list2
#       list2 - list in which to find sublist
# Returns: True iff all the elements in list1 are in list2
def dominated(list1, list2): return list1 == [i for i in list1 if i in list2]

def solvePetrick(epis, uncovered, coveredBy, numVars):
    if debug: print "Punting on Petrick's method (uncovered != [])"
    if debug: print "uncovered=%s" % uncovered
    if debug: print "coveredBy=%s" % coveredBy
    # uncovered is a list of the minterms not covered by EPIs

    # coveredBy is an dictionary of arrays of prime implicants indexed by the
    # minterm those prime implicants cover
    # e.g. {0: [[0, 1], [0, 2]], 1: [[0, 1], [1, 5]], 2: [[0, 2], [2, 6]], 
    #       5: [[1, 5], [5, 7]], 6: [[2, 6], [6, 7]], 7: [[5, 7], [6, 7]]} 

    # create an array of all the PIs which cover the uncovered minterms
    flatCoveredBy = []
    for minterm in uncovered:
        for pi in coveredBy[minterm]:
            if pi not in flatCoveredBy: flatCoveredBy += [pi]

    if debug: print "flatCoveredBy=%s" % flatCoveredBy

    if len(flatCoveredBy) > 26: print "Cannot handle more than 26 prime implicants for Petrick's method"

    # labels for each PI in Petrick's method
    labels = [chr(i + ord('A')) for i in range(len(flatCoveredBy))]

    # array of costs for each PI, in same order as labels
    costs  = [numVars - log(len(pi), 2) for pi in flatCoveredBy]
    if debug: print "costs=%s" % costs

    #
    # Form Petrick equation based on PIs
    #

    expressions = ["(" for i in range(len(uncovered))] 
    # array to represent Petrick equation e.g. ["(A | B)", "(C | ~D)"]...

    for i, pi in enumerate(flatCoveredBy):
        for j, minterm in enumerate(uncovered):
            if minterm in pi: # the pi covers that minterm
                expressions[j] += labels[i]
                expressions[j] += " | "

    equation = ""
    for i in range(len(expressions)):
        expressions[i] = expressions[i][:-3] # remove trailing " | "
        expressions[i] += ")"
        equation += expressions[i]
        equation += " & "

    equation = equation[:-3] # remove trailing " & "
    if debug: print "equation=%s" % equation

    # NOTE: If equation is only one term sum term, it cannot be simplified,
    # and doing so introduces a bug - detect this and short circuit

    products = []
    if "&" in equation: # more than one term
        if debug: print "simplify=%s" % simplify_logic(equation, 'dnf')
        simplified = str(simplify_logic(equation, 'dnf'))[3:-1] # leave only And terms

        simplified = ''.join(simplified.split()).replace(',','').split('And')

        if debug: print "simplified=%s" % simplified

        for term in simplified:
            if debug: print "term=%s" % term

            if len(term) > 0:
                # there is a special case when simplify_logic yields
                # e.g. Or(And(A, C, D), B) causing a term of the form
                # (ACD)B (or A(CDB)) => check if beginning or end
                # is '(' or ')'
                if not term.startswith('('): # A(CDB) case
                    products += [i.replace(')', '') for i in term.split('(')]
                elif not term.endswith(')'): # (ACD)B case
                    products += [i.replace('(', '') for i in term.split(')')]
                else:                        # (ABCD) case
                    products += [term.replace("(","").replace(")","")]

        if debug: print "products=%s" % products
    else: products = equation[1:-1].split(" | ") # only one term

    # ---------------------------------------------------------------------
    # Find cheapest term
    # ---------------------------------------------------------------------

    product_costs = [0 for i in range(len(products))]
    for i, product in enumerate(products):
        for pi in product:
            product_costs[i] += costs[ord(pi) - ord('A')]
        product_costs[i] += 1 # for and gate

    if debug: print "product_costs=%s" % product_costs
    # product_costs: e.g. [9, 9, 7, 9, 7] - array of costs for each product term

    # so choose min cost term
    minCostTerms = []

    for i, product_cost in enumerate(product_costs):
        if product_cost == min(product_costs): minCostTerms.append(products[i])
    if debug: print "minCostTerms=%s" % minCostTerms

    # ---------------------------------------------------------------------
    # Add minCostTerms PIs as EPIs
    # ---------------------------------------------------------------------

    setOfEpis = [list(epis) for i in range(len(minCostTerms))]

    for i, term in enumerate(minCostTerms):
        for pi in term:
            if debug: print "pi=%s, term=%s, i=%s flatCoveredBy=%s (%s)" % (pi, term, i, flatCoveredBy[ord(pi) - ord('A')], str(mintermsToLiterals(flatCoveredBy[ord(pi) - ord('A')], numVars)))
            # convert label back into list of minterms it labels, and add to EPIs
            setOfEpis[i] += [flatCoveredBy[ord(pi) - ord('A')]]

    if debug: print "setOfEpis=%s" % setOfEpis
    return [[mintermsToLiterals(pi, numVars) for pi in epis] for epis in setOfEpis]

# -----------------------------------------------------------------------------
# MINIMIZE

# Args: ones - the minterms of the function
#       dcs  - the don't cares of the function
# Returns: array of strings representing close cover
#          e.g. { '1X0', 'XX0', ... }
# Notes: All minterms which are not in ones or dcs are assumed zeros
# This interface is deliberately similar to the qm library for testing purposes
# -----------------------------------------------------------------------------
def minimize(ones=[], dc=[], numVars=0):
    if len(ones) < 1:
        sys.stderr.write("ones array too short (ones=%s) or numVars too low (numVars=%s)\n" % (ones, numVars))
        return {}

    # represent all minterms as binary strings padded w/ leading 0s
    zeroCubes = [bin(i)[2:].zfill(numVars) for i in ones+dc]

    nonEpis = [literalsToMinterms(pi) for pi in generatePis(zeroCubes)]
    if debug: print "primeImplicants=%s" % nonEpis
    # prime implicants as lists of minterms

    # -------------------------------------------------------------------------
    # Form close cover
    # -------------------------------------------------------------------------

    # everything starts uncovered
    uncovered = list(ones)
    epis      = []

    if debug: print "ONES=%s" % ones

    while uncovered is not []:
        if debug: print "uncovered=%s (in loop)" % uncovered
        # initialize empty dict to store number of covers for a given minterm
        coveredBy = {}
        for minterm in uncovered: coveredBy[minterm] = [] 

        if debug: print "nonEpis=%s (in loop)" % nonEpis
        for pi in nonEpis:
            for minterm in pi:
                # only count minterms that haven't been covered, not dont cares
                if minterm in uncovered: coveredBy[minterm] += [pi]
        if debug: print "coveredBy=%s (in loop)" % coveredBy

        if debug: print "CHECKING FOR EPIS"
        if debug: print "uncovered=%s" % uncovered

        # ---------------------------------------------------------------------
        # Search for EPIs
        # ---------------------------------------------------------------------
        foundEpi = False
        for minterm in uncovered:
            if debug: print "minterm=%s" % minterm
            if len(coveredBy[minterm]) == 1: # only covered by one prime implicant, so EPI
                epis += coveredBy[minterm]
                if debug: print "epis=%s (+= %s)" %(epis, coveredBy[minterm])
                nonEpis.remove(coveredBy[minterm][0]) 

                for minterm in coveredBy[minterm][0]:  # check all minterms EPI covers
                    if minterm in uncovered: uncovered.remove(minterm)
                foundEpi = True

        # ---------------------------------------------------------------------
        # Find dominating rows
        # ---------------------------------------------------------------------
        if not foundEpi:
            foundDomRow = False
            if debug: print "SEARCHING FOR DOMINATING ROWS"
            if debug: print "coveredBy=%s" % coveredBy
            for minterm in uncovered:
                size = len(coveredBy[minterm])
                for i in range(size):
                    for j in range(i + 1, size):
                        pi1 = coveredBy[minterm][i]
                        pi2 = coveredBy[minterm][j]
                        l1 = [x for x in pi1 if x in uncovered]
                        l2 = [x for x in pi2 if x in uncovered]

                        if debug: print "COMPARING (for minterm = %s) l1=%s (implicant=%s) to l2=%s (implicant=%s)" % (minterm, l1, pi1, l2, pi2)

                        if dominated(l2, l1):
                            if debug: print "FOUND DOMINATING ROW: l2=%s dominated by l1=%s" % (l2, l1)
                            if pi2 in nonEpis: nonEpis.remove(pi2)
                            foundDomRow = True
                        elif dominated(l1, l2):
                            if debug: print "FOUND DOMINATING ROW: l1=%s dominated by l2=%s" % (l1, l2)
                            if pi1 in nonEpis: nonEpis.remove(pi1)
                            foundDomRow = True
            if not foundDomRow:
                if debug: print "FOUND NO DOMINATING ROWS"
                break # no dominating rows, but uncovered PIs so try Petrick's

    if debug: print "epis=%s" % epis
    if debug: print [[mintermsToLiterals(pi, numVars) for pi in epis]]
    if debug: print "nonEpis=%s" % nonEpis

    # -------------------------------------------------------------------------
    # Petrick's method!
    # -------------------------------------------------------------------------

    if uncovered != []: return solvePetrick(epis, uncovered, coveredBy, numVars)
    else:               return [[mintermsToLiterals(pi, numVars) for pi in epis]]

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    for func in sys.stdin:
        (ones, dcs) = parse_func(func)
        numvars     = int(ceil(log(max(ones+dcs) + 1, 2)))


        if True:
            minimization = minimize(ones, dcs, numvars)
            lib_res      = qm.qm(ones=ones, dc=dcs)

            # ensure order doesn't matter
            lib_res.sort()
            for mini in minimization: mini.sort()

            if any([result == lib_res for result in minimization]):
                #print minimization[0]
                #nice_print(minimization[0])
                sys.stdout.write(".")
                sys.stdout.flush()
            else:
                #print "Results differed"
                #minimization[0].sort
                #print "minimization=%s" % minimization
                #nice_print(minimization[0])
                #lib_res.sort
                #print "lib_res=%s" % lib_res
                #nice_print(lib_res)
                sys.stdout.write("F")
                sys.stdout.write(": Failed on func = |%s|" % func)
        else:
            # ---------------------------------------------------------------------
            # Compute SOP
            # ---------------------------------------------------------------------
            minimization = minimize(ones, dcs, numvars)
            nice_print(minimization, numvars, sop=True)

            zeros = [maxterm for maxterm in range(2**numvars) if maxterm not in ones]
            dcs   = [dc for dc in dcs if dc not in zeros]

            # ---------------------------------------------------------------------
            # Compute POS
            # ---------------------------------------------------------------------
            minimization = minimize(zeros, dcs, numvars)
            nice_print(minimization, numvars, sop=False)


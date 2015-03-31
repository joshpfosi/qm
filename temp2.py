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
    return [[mintermsToLiterals(pi, numVars) for pi in epis] for epis in setOfEpis][0]

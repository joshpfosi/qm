# Python library to compute the SOP minimization of a given boolean
# function

__author__ = "Josh Pfosi"

# Args: func - string defining minterms and don't cares
# Returns: dict w/ ones and dc elements
# Notes: This correctly parses desired input but will fail silently on
# poorly formed input
def parse_func(func):
    # remove all whitespace characters
    func = ''.join(func.split())

    ones = func
    dcs  = []

    if "+" in func:
        (ones, dcs) = func.split('+')
        dcs  = [int(i) for i in dcs[2:-1].split(',')]

    # list comprehension to remove 'm(' and ')'
    # and cast to array of integers
    ones = [int(i) for i in ones[2:-1].split(',')]

    return (ones, dcs)

def pretty_print(result=[]):
    if len(result) < 1: return

    num_vars = len(result[0])
    
    if num_vars > 10:
        print "Cannot handle more than 10 variables"
        return

    variables = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']

    sop = pos = ""

    for epi in result:
        pos += "("

        while epi.endswith("X"): epi = epi[:-1] # leave off trailing dont cares

        for i, lit in enumerate(epi): # use enumerate to expose i
            if lit is "X": continue

            if lit is "1": 
                sop += variables[i]
                pos += "%s'+" % variables[i]
            elif lit is "0":
                sop += "%s'" % variables[i]
                pos += "%s+" % variables[i]

        sop += "+"
        pos = pos[:-1] + ")" # replace last plus with ')'

    sop = sop[:-1]

    print "=%s" % sop
    print "=%s" % pos

# Args: ones - the minterms of the function
#       dcs  - the don't cares of the function
# Returns: array of strings representing close cover
#          e.g. { '1X0', 'XX0', ... }
# Notes: All minterms which are not in ones or dcs are assumed zeros
# This interface is deliberately similar to the qm library for testing purposes
def minimize(ones=[], dc=[]):
    if len(ones) < 1:
        return {}

    return qm.qm(ones=ones, dc=dc)

if __name__ == "__main__":
    import qm
    import sys
    from numpy.random import randint
    from numpy import unique

    for func in sys.stdin:
        (ones, dc) = parse_func(func)

        # calculate both
        lib_res = qm.qm(ones=ones, dc=dc)
        my_res  = minimize(ones=ones, dc=dc)

        # ensure order doesn't matter
        lib_res.sort()
        my_res.sort()

        if lib_res == my_res:
            print my_res
            pretty_print(my_res)
        else:
            print "Results differed"

        # test and print
        #if lib_res == my_res:
        #  sys.stdout.write(".")
        #else:
        #  sys.stdout.write("F")



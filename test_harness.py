# Python script to import and test EE 26 students implementations of QM
# algorithm via a standard interface
#
# Usage: python test_harness.py < inputfile

__author__ = "Josh Pfosi"

if __name__ == "__main__":
    import qm
    import sys
    from math import *
    from minimize_final import *

    moduleNames = [] 
    modules = map(__import__, moduleNames)

    for func in sys.stdin:
        (ones, dcs) = parseFunc(func)
        numvars     = int(ceil(log(max(ones+dcs) + 1, 2)))

        solutions = []

        # Library implementation
        solutions += [nicePrint(qm.qm(ones=ones, dc=dcs), numvars, sop=True)]

        # My implementation
        solutions += [nicePrint(minimize(ones, dcs, numvars), numvars, sop=True)]

        for module in modules:
            solutions += [nicePrint(module.minimize(ones, dcs, numvars), numvars, sop=True)]

        for i, sol in enumerate(solutions):
            solution = sol.split("+")
            solution.sort()
            solutions[i] = "+".join(solution)

        sys.stdout.write("%s (reference answer)\n" % solutions[0])
        sys.stdout.write("%s (my answer)\n" % solutions[1])

        for i, sol in enumerate(solutions[2:]): 
            sys.stdout.write("%s (from %s)\n" % (solutions[i], modules[i].__name__))

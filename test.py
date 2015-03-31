# Failures

#m(0,1,3,4,7,11,12,15,16,17,20,28)
#m(19, 14, 4, 16, 6, 18, 7, 13, 10, 17, 5, 0)+d(3, 9, 15)
#m(1,2,3,4,5,6,7,8,9,10,11,12,13,14)
#m(0,128)

# Differed but verified
# m(13, 3, 8, 4, 5, 2, 16, 7, 6, 10, 11, 18, 17, 19)+d(0, 9, 15, 14)

if __name__ == "__main__":
    from minimize_final import *
    from numpy import *

    # generate lots of test input

    numFuncs = 10 # generate numFuncs inputs at once
    maxVal   = 20 # no minterm can exceed this amt

    # array of sizes of ones arrays
    sizes = [int(maxVal * random.random()) for i in xrange(numFuncs)]

    funcs = []
    for size in sizes:
        a1 = [int(maxVal * random.random()) for i in xrange(size)]
        # create a size sized array of numbers between 0 and maxVal
        a2 = [int(maxVal * random.random()) for i in xrange(int(random.random() * size))]
        # create a randomly sized subset of dcs

        ones = []
        dcs  = []

        for elem in a1:
            if elem not in ones: ones.append(elem)

        for elem in a2:
            if elem not in dcs and elem not in ones: dcs.append(elem)

        if len(ones) != 0:
            if len(dcs) != 0:
                funcs += ["m({0})+d({1})".format(str(ones)[1:-1], str(dcs)[1:-1])]
            else: 
                funcs += ["m({0})".format(str(ones)[1:-1])]

    succ = open('big_test.txt', 'a')
    fail = open('big_fail.txt', 'a')
    for func in funcs:
        (ones, dc) = parse_func(func)

        # calculate both
        lib_res       = qm.qm(ones=ones, dc=dc)
        minimizations = minimize(ones=ones, dc=dc)
        # returns an array of minimizations if multiple same cost terms exist

        # ensure order doesn't matter
        lib_res.sort()
        for minimization in minimizations: minimization.sort()

        if any([result == lib_res for result in minimizations]):
            succ.write("%s\n" % func)
            #print minimizations[0]
            #nice_print(minimizations[0])
            sys.stdout.write(".")
        else:
            fail.write("%s\n" % func)
            #print "Results differed"
            #print "minimizations=%s" % minimizations
            #print "lib_res=%s" % lib_res
            sys.stdout.write("F")
            #sys.stdout.write(": Failed on func = |%s|" % func)

    print "\n"



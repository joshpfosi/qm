# Python library to compute the SOP minimization of a given boolean
# function

__author__ = "Josh Pfosi"

# Args: ones - the minterms of the function
#       dcs  - the don't cares of the function
# Notes: All minterms which are not in ones or dcs are assumed zeros
# This interface is deliberately similar to the qm library for testing purposes
def minimize(ones=None, dc=None):
  return qm.qm(ones=ones, dc=dc)

if __name__ == "__main__":
  import qm
  import sys
  from numpy.random import randint
  from numpy import unique

  ones = [0,1,4,7,4]
  dc   = []

  for i in range(0,3):
    # calculate both
    lib_res = qm.qm(ones=ones, dc=dc)
    my_res  = minimize(ones=ones, dc=dc)
    
    # ensure order doesn't matter
    lib_res.sort()
    my_res.sort()

    # test and print
    if lib_res == my_res:
      sys.stdout.write(".")
    else:
      sys.stdout.write("F")



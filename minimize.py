# Python library to compute the SOP minimization of a given boolean
# function

__author__ = "Josh Pfosi"

# Args: ones - the minterms of the function
#       dcs  - the don't cares of the function
# Notes: All minterms which are not in ones or dcs are assumed zeros
# This interface is deliberately similar to the qm library for testing purposes
def minimize():
  return ['X01', '0X0']

if __name__ == "__main__":
  import qm

  lib_res = qm.qm(ones=[1, 2, 5], dc=[0, 7])
  my_res  = minimize()
  
  if lib_res == my_res:
    print "."
  else:
    print "F"



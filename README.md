# Quine McCluskey Python Implementation

This is a Python implementation of a naive Boolean function minimizer for my Digital Logic Systems (EE 26) course.

## Usage

```
python minimize.py
```

The program accepts input on `stdin` in the form `m(<minterms>)+d(<dont cares>)` e.g. 

```
m(0,2,5,7,8,10,13,15)+d(1,3,9,11)
m(4,5,10,11,13,15)
m(3,4)+d(1,7)
```

and outputs the minimized solution in SOP and POS form. The above input yields:

```
=B'+D
=(B'+D)
=A'BC'+AB'C+ABD
=(A+C')(B+C)(A'+B'+D)
=AB'C'+A'C
=(A+C)(B'+C)(B+C')
```

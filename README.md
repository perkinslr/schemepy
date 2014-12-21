schemepy
========

Implementation of scheme in python supporting call/cc and hygienic macros

Using schemepy
--------------
There are 3 basic ways to use schemepy.  As a stand-alone scheme interpreter:
    # /usr/bin/schemepy <script.scm>

As a stand-alone REPL:
    # /usr/bin/schemepy
    schemepy> 


Or from inside a python script
    import scheme
    scheme.repl.repl()
    schemepy> 

Or to run predefind strings from python
    import scheme
    scheme.eval.Eval(myString)
    #or
    scheme.eval.Eval(myFile)

Eval will only execute the first statement in its input, so if you want compound inputs, wrap them with 
    (begin )



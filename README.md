schemepy
========

Implementation of scheme in python supporting call/cc and hygienic macros

Using schemepy
---------

There are 3 basic ways to use schemepy.  As a stand-alone scheme interpreter:

    $ /usr/bin/schemepy <script.scm>

As a stand-alone REPL:

    $ /usr/bin/schemepy
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

The default environment setup is controlled in builtins.py, with 
additional definitions in builtins.scm (scheme/builtins.scm in the 
source, /usr/share/schemepy/stdlib/builtins.scm once installed). 

Scheme is sandboxed away from python, so only functions provided into 
the global Environment (scheme.Globals.Globals) or some other scheme 
environment can be accessed.  Note that by default, the interpreter is 
given access to the file system and other sensitive functions.  If you 
want to use it as a sandbox for user code, you need to strip out 
anything you don't want called.  Also, getattr and getitem are 
undefined in the default environment.  If you are running trusted 
code, you can simply add the standard getattr to the global 
Environment.  If you are running user code, and want to provide 
getattr, write one that only allows access to approved data types:

    def safegetattr(obj, attr):
        if isinstance(obj, some_class):
            return getattr(obj, attr)
        raise TypeError("getattr only supports objects of type %r" % some_class)

or similar.

Differences from r5rs scheme
---------

Macro expansion is mixed with code execution.  Normally macro 
expansion would be done at compile time, but
for simplicity each statement is expanded right before execution.  By 
itself, the only effect this has is on performance.

Macros are first-class objects.  Normally, macros and normal 
procedures are essentially the same, except that macros' names are 
listed in a MacroTable, while procedures are listed in the normal 
variable table.  I don't maintain a separate list of macros, so an 
object being a macro is recorded on the object itself.  Normally, this 
isn't noticable, as any code which wouldn't generate errors in racket 
should produce the same output (This is done by making 
define-syntax take either a macro or a procedure and wrap it in a 
macro, which calls the wrapped object with the syntax and expects the 
return type to be syntax), but it does open the door to some things 
which scheme users won't expect.

    (define some-macro #f)
    (define (somefun) 
        (define-syntax junk (lambda (x) #'(+ 1 2)))
        (set! some-macro junk)
    )
    (somefun) (some-macro)
    ;3


Tail recursion and general Tail-Call-Optimisation
---------

Tail recursion is not handled differently from other tail calls; but, 
TCO is partially supported.  Some calls recursively call process(), 
which breaks TCO, but most calls are properly TC optimised.



Booleans
---------

Truth values follow python's convention rather than scheme's (0, 
False, None, (), and '' are false, or anything which provides a 
__bool__ method which returns False).  If you need scheme's behaviour, 
simply rewrite eq? and what not to check for identity against False.

#! /usr/bin/python2.7
# Cribbed from Peter Norvig's scheme interpreter in python, http://norvig.com/lispy2.html


# ############### Tests for lis.py and lispy.py
import sys,os
sys.path.append(os.getcwd())
import scheme.symbol
import scheme.procedure


lis_tests = [
    ("(quote (testing 1 (2.0) -3.14e159))", ['testing', '1', ['2.0'], '-3.14e159']),
    ("(+ 2 2)", 4),
    ("(+ (* 2 100) (* 1 10))", 210),
    ("(if (> 6 5) (+ 1 1) (+ 2 2))", 2),
    ("(if (< 6 5) (+ 1 1) (+ 2 2))", 4),
    ("(define x 3)", None), ("x", 3), ("(+ x x)", 6),
    ("(begin (define x 1) (set! x (+ x 1)) (+ x 1))", 3),
    ("((lambda (x) (+ x x)) 5)", 10),
    ("(define twice (lambda (x) (* 2 x)))", None), ("(twice 5)", 10),
    ("(define compose (lambda (f g) (lambda (x) (f (g x)))))", None),
    ("((compose list twice) 5)", [10]),
    ("(define repeat (lambda (f) (compose f f)))", None),
    ("((repeat twice) 5)", 20), ("((repeat (repeat twice)) 5)", 80),
    ("(define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))", None),
    ("(fact 3)", 6),
    ("(fact 50)", 30414093201713378043612608166064768844377641568960512000000000000),
    ("(define abs (lambda (n) ((if (> n 0) + -) 0 n)))", None),
    ("(list (abs -3) (abs 0) (abs 3))", [3, 0, 3]),
    ("""(define combine (lambda (f)
    (lambda (x y)
      (if (null? x) (quote ())
          (f (list (car x) (car y))
             ((combine f) (cdr x) (cdr y)))))))""", None),
    ("(define zip (combine cons))", None),
    ("(zip (list 1 2 3 4) (list 5 6 7 8))", [[1, 5], [2, 6], [3, 7], [4, 8]]),
    ("""(define riff-shuffle (lambda (deck) (begin
        (define take (lambda (n seq) (if (<= n 0) (quote ()) (cons (car seq) (take (- n 1) (cdr seq))))))
        (define drop (lambda (n seq) (if (<= n 0) seq (drop (- n 1) (cdr seq)))))
        (define mid (lambda (seq) (/ (length seq) 2)))
        ((combine append) (take (mid deck) deck) (drop (mid deck) deck)))))""", None),
    ("(riff-shuffle (list 1 2 3 4 5 6 7 8))", [1, 5, 2, 6, 3, 7, 4, 8]),
    ("((repeat riff-shuffle) (list 1 2 3 4 5 6 7 8))", [1, 3, 5, 7, 2, 4, 6, 8]),
    ("(riff-shuffle (riff-shuffle (riff-shuffle (list 1 2 3 4 5 6 7 8))))", [1, 2, 3, 4, 5, 6, 7, 8]),
    ("(and (begin 0) 6)", 0),
]

lispy_tests = [
    ("()", SyntaxError),
    ("(set! x)", IndexError),
    ("(define 3 4)", None),
    ("(define 3 (- 3 1))", None),
    ("(quote 1 2)", SyntaxError),
    ("(if 1 2 3 4)", SyntaxError),
    ("(lambda (x))", scheme.procedure.SimpleProcedure),
    ("""(if (= 1 1) (define-macro (a b) a)
          (define-macro a (quote b)))""", None),
    ("(define (twice x) (* 2 x))", None),
    ("(twice 2)", 4),
    ("(twice 2 2)", TypeError),
    ("(define lyst (lambda items items))", None),
    ("(lyst 1 2 3 (+ 2 2))", [1, 2, 3, 4]),
    ("(if 1 2)", 2),
    ("(if (= 3 4) 2)", False),
    ("(define ((account bal) amt) (set! bal (+ bal amt)) bal)", None),
    ("(define a1 (account 100))", None),
    ("(a1 0)", 100), ("(a1 10)", 110), ("(a1 10)", 120),
    ("""(define (newton guess function derivative epsilon)
    (define guess2 (- guess (/ (function guess) (derivative guess))))
    (if (< (abs (- guess guess2)) epsilon) guess2
        (newton guess2 function derivative epsilon)))""", None),
    ("""(define (square-root a)
    (newton 1 (lambda (x) (- (* x x) a)) (lambda (x) (* 2 x)) 1e-8))""", None),
    ("(> (square-root 200.) 14.14213)", True),
    ("(< (square-root 200.) 14.14215)", True),
    ("(= (square-root 200.) (sqrt 200.))", True),
    ("""(define (sum-squares-range start end)
         (define (sumsq-acc start end acc)
            (if (> start end) acc (sumsq-acc (+ start 1) end (+ (* start start) acc))))
         (sumsq-acc start end 0))""", None),

    ("(call/cc (lambda (throw) (+ 5 (* (throw 1) 10 )))) ;; throw", 1),
    # ("(sum-squares-range 1 3000)", 9004500500), ## Tests tail recursion
    ("(call/cc (lambda (throw) (+ 5 (* 10 1)))) ;; do not throw", 15),
    ("""(call/cc (lambda (throw) 
         (+ 5 (* 10 (call/cc (lambda (escape) (* 100 (escape 3)))))))) ; 1 level""", 35),
    ("""(call/cc (lambda (throw) 
         (+ 5 (* 10 (call/cc (lambda (escape) (* 100 (throw 3)))))))) ; 2 levels""", 3),
    ("""(call/cc (lambda (throw) 
         (+ 5 (* 10 (call/cc (lambda (escape) (* 100 1))))))) ; 0 levels""", 1005),
    ("(* 1i 1i)", -1), ("(sqrt -1)", 1j),
    ("(let ((a 1) (b 2)) (+ a b))", 3),
    ("(let ((a 1) (b 2 3)) (+ a b))", SyntaxError),
    ("(and 1 2 3)", 3), ("(and (> 2 1) 2 3)", 3), ("(and)", True),
    ("(and (> 2 1) (> 2 3))", False),
    (
        "(define-macro (unless . args) (display 'xyzzy) (display args) "
        "(quasiquote (if (not ,(car args)) (begin ,@(cdr args))))) ; test `",
        None),
    ("(unless (= 2 (+ 1 1)) (display 2) 3 4)", False),
    (r'(unless (= 4 (+ 1 1)) (display 2) (display "\n") 3 4)', 4),
    ("(quote x)", 'x'),
    ("(quote (1 2 three))", ['1', '2', 'three']),
    ("'x", 'x'),
    ("'(one 2 3)", ['one', '2', '3']),
    ("(define L (list 1 2 3))", None),
    ("`(testing ,@L testing)", ['testing', 1, 2, 3, 'testing']),
    ("`(testing ,L testing)", ['testing', [1, 2, 3], 'testing']),
    ("`,@L", IndexError),
    ("""'(1 ;test comments '
     ;skip this line
     2 ; more ; comments ; ) )
     3) ; final comment""", ['1', '2', '3']),
    ('''(defmacro (for x in l . calls) (for-each (lambda (,x) ,@calls) ,l))''', None),
    ('''(define tst (lambda (x) (syntax (+ 1 2))))''', None),
    ('''(tst 5)''', ['+','1','2']),
    ('''(define-syntax tst (lambda (x) (syntax (+ 1 2))))''', None),
    ('''(tst 5)''', 3),
    ('''(define-syntax when
            (lambda (x)
                (syntax-case x ()
                    ((_ test e e* ...)
                        (syntax (if test (begin e e* ...)))))))''', None),
    ('''(when (< 0 5) "true")''', "true"),
    ('''(when (> 0 5) "true")''', False),
    ('''(let-syntax ((s (lambda (x) #'(+ 1 2)))) (+ 5 (s)))''', 8),
    # ('''(for x in '(1 2 3) x)''', 3)
]


def test(tests, name=''):
    import scheme.Globals
    "For each (exp, expected) test case, see if eval(parse(exp)) == expected."
    fails = 0
    for (x, expected) in tests:
        try:
            result = Eval(x)
            if isinstance(result, scheme.symbol.Symbol):
                if result.isBound(scheme.Globals.Globals):
                    result = result.toObject(scheme.Globals.Globals)
            print x, '=>', repr(result)
            ok = (result == expected) or expected is None
            if not ok and type(expected) == type:
                if isinstance(result, expected):
                    ok = True
        except Exception as e:
            p.dumpStack()
            print x, '=raises=>', type(e).__name__, e
            ok = type(expected) == type and issubclass(expected, Exception) and isinstance(e, expected)
        if not ok:
            fails += 1
            print 'FAIL!!!  Expected', expected
    print '%s %s: %d out of %d tests fail.' % ('*' * 45, name, fails, len(tests))


if __name__ == '__main__':
    from scheme.eval import Eval, p
    test(lis_tests + lispy_tests, 'lispy.py')

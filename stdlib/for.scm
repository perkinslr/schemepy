(begin 
    (define (for-each callable lst)
        (define ret (callable (car lst)))
        (if (cdr lst) (for-each callable (cdr lst)) ret))


    (defmacro (for x in l . calls) (for-each (lambda (,x) ,@calls) ,l))
)

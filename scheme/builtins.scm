(begin
    (define (for-each callable lst)                                                      
        (define ret (callable (car lst)))
        (if (cdr lst) (for-each callable (cdr lst)) ret))
    
    (define-macro and (lambda args 
        (if (null? args) #t
            (if (= (length args) 1) (car args)
                `(if ,(car args) (and ,@(cdr args)) #f)))))
    
    (define (newline) (display "~n"))
    
    (define-macro (+= var val) (set! var (+ var val)))
    
    (define-macro (++ var) (+= var 1))


    (define (print . args)
	(for-each (lambda (x) (display x) (display " ")) args)
	(display "~n"))
	(define else #t)
)

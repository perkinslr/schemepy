(begin
    (define (for-each callable lst)
        (callable (car lst)) (for-each callable (cdr lst)))
    (define (andl params)
        (display params)
        (display (type params))
        (if (null? params) #t
                (if (car params) (if (= 1 (len? params)) (car params) (andl (cdr params))) (car params))))
    
    (define-macro (and . params)
        (andl params))
    
    (define (newline) (display "~n"))
    (define-macro (+= var val) (set! var (+ var val)))
    (define-macro (++ var) (+= var 1))
)

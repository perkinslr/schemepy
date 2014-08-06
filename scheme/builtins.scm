(begin
    (define (for-each callable lst)
        (callable (car lst)) (for-each callable (cdr lst)))
    
    (define (andl params)
        
        
        (if (null? params) 
            #t
            (if (bool (car params) )
                (if (= 1 (len? params)) 
                    (car params) 
                    (andl (cdr params)))
                (car params))))

    (define (and . params)
        
        (andl params))
    
    (define (newline) (display "~n"))
    
    (define-macro (+= var val) (set! var (+ var val)))
    
    (define-macro (++ var) (+= var 1))
    (display 28)
    (newline)
    (display and)
)

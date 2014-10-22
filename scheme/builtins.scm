(begin
    (define (for-each callable lst)                                                      
        (define ret (callable (car lst)))
        (if (cdr lst) (for-each callable (cdr lst)) ret))
    
    (defmacro (for x in l . calls) (for-each (lambda (x) ,@calls) ,l))
    
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

    (define (build-table header the-list)
        (output "<table>")
        (for-each
            (lambda (header) (output "<th>" header "</th>"))
            header)
        (for-each
            (lambda (row)
            (output "<tr>")
            (for-each
                (lambda (col) (output "<td>" (if (callable col) (col) col) "</td>"))
                row)
            (output "</tr>"))
        the-list)
        (output "</table>"))


)

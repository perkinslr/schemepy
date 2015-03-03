(begin 
    (define-syntax let
    	(syntax-rules ()
    		((let ((name value) ...) body ...) ((lambda (name ...) body ...) value ...))
    		((let function-name ((name value) ...) body ...)
    			(let ()
    				(begin
    				(define function-name (lambda (name ...) body ...))
    				(function-name value ...))))))
    
    
    (define-syntax let*
    (syntax-rules ()
    	((let* () body ...)(let () body ...))
    	((let* ((name1 val1) (name2 val2) ...) body ...)
    	(let ((name1 val1))
    	(let* ((name2 val2) ...)
    		body ...)))))
    
    
    (define (print . args)
    		(for-each (lambda (x) (display x) (display " ")) args)
    		(display "~n"))

)

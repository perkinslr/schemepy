(define (print . args)
        (for-each (lambda (x) (display x) (display " ")) args)
        (display "~n"))

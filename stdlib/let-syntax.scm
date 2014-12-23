(define-syntax let-syntax 
    (syntax-rules () 
    ((let-syntax () body ...) (begin body ...))
    ((let-syntax ((name transformer)) body ...) (let () (begin (define-syntax name transformer) body ...)))
    ((let-syntax ((name transformer) more ...) body ...) (let () (begin (define-syntax name transformer) (let-syntax (more ...) body ...))))))


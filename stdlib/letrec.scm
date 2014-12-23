(define-syntax letrec
  (syntax-rules ()
    ((letrec ((var1 init1) ...) body ...)
     (letrec "generate temp names"
       (var1 ...)
       ()
       ((var1 init1) ...)
       body ...))
    ((letrec "generate temp names"
       ()
       (temp1 ...)
       ((var1 init1) ...)
       body ...)
     (let ((var1 <undefined>) ...)
       (let ((temp1 init1) ...)
         (set! var1 temp1)
         ...
         body ...)))
    ((letrec "generate temp names"
       (x y ...)
       (temp ...)
       ((var1 init1) ...)
       body ...)
     (letrec "generate temp names"
       (y ...)
       (newtemp temp ...)
       ((var1 init1) ...)
       body ...))))

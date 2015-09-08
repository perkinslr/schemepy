#encoding: scheme_encode
"""lines beginning with ! execute i the scheme environment
The encoding must be copied/linked to <python_install>/encodings"""
print 5

!(define (double x) (+ x x))

for i in range(10):
   !(print (double 5))



if __name__=='__main__':
    exit(
        !(double 1)
        )


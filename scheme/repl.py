from Queue import Empty


__author__ = 'perkins'


from scheme.parser import Parser
import scheme.processer
processer = scheme.processer.processer
import sys

def repl(f=sys.stdin, prompt='schemepy> ', of=sys.stdout):
    global parser
    parser = Parser(f)
    while True:
        sys.stdout.write(prompt)
        ast = parser.ast
        if ast:
            try:
                r = processer._process(ast)
            except Empty as e:
                r = e.ret
            except Exception as e:
                r=e
            if r is not None and of:
                print >> of, r
        else:
            break
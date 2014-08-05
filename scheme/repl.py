__author__ = 'perkins'


from scheme.parser import Parser
import scheme.processer
processer = scheme.processer.processer
import sys

def repl(f=sys.stdin):
    global parser
    parser = Parser(f)
    while True:
        sys.stdout.write('schemepy> ')
        ast = parser.ast
        if ast:
            r = processer.process(ast)
            if r is not None:
                print r
        else:
            break
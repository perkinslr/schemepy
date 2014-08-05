from __future__ import division
import re
import cStringIO

from symbol import Symbol
from token import Token


class Parser(object):
    tokenizer = r"""\s*(,@|[('`,)]|"(?:[\\].|[^\\"])*"|;.*|[^\s('"`,;)]*)(.*)"""
    eof_object = Symbol('#<eof-object>')
    eol_object = Symbol('#<eol-object>')
    @classmethod
    def stringParser(cls, string):
        return cls(cStringIO.StringIO(string))
    def __init__(self, _file):
        self.file = _file;
        self.line = ''
    @property
    def tokens(self):
        """Return the next token, reading new text into line buffer if needed."""
        while True:
            if self.line=='\n' or self.line=='':
                self.line = self.file.readline()
            if self.line == '':
                break

            # noinspection PyUnresolvedReferences
            token, self.line = re.match(self.tokenizer, self.line).groups()
            if token != '' and not token.startswith(';'):
                yield Token(token)
            if self.line=='\n' or self.line=='':
                yield self.eol_object
        yield self.eof_object
    @property
    def ast(self):
        tokens=self.tokens
        o = []
        def read_ahead(token):
            if '(' == token:
                L = []
                while True:
                    token = tokens.next()
                    if token is self.eof_object:
                        raise SyntaxError('unexpected EOF in list')
                    if token is self.eol_object:
                        continue
                    if token == ')':
                        return L
                    else:
                        L.append(read_ahead(token))
            elif ')' == token:
                raise SyntaxError('unexpected )')
            elif token is self.eol_object:
                raise SyntaxError('unexpected eol')
            else:
                return token.symbol
        for t in tokens:
            if t is self.eof_object:
                return o
            if t is self.eol_object:
                if o:
                    return o
                continue
            o.append(read_ahead(t))




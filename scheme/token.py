from symbol import Symbol


class Token(unicode):
    def setLine(self, l):
        self.line=l
        return self
    @property
    def symbol(self):
        """


        :return: Symbol
        """
        return Symbol(self).setLine(self.line)

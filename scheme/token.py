from symbol import Symbol


class Token(unicode):
    @property
    def symbol(self):
        """


        :return: Symbol
        """
        return Symbol(self)

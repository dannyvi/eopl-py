import itertools


class Symbol:
    def __init__(self, symbol):
        self.symbol = symbol

    def __repr__(self):
        return self.__str__()

    def __format__(self, format_spec):
        return format(self.__str__(), format_spec)

    def __eq__(self, other):
        return type(self) == type(other) and self.symbol == other.symbol

    def __len__(self):
        return len(self.__str__())

    def __hash__(self):
        return hash(self.__str__())


class NTerm(Symbol):
    def __init__(self, symbol, nullable=False):
        self.symbol = symbol
        self.nullable = nullable

    def __str__(self):
        if self.nullable:
            return f"{self.symbol}"
            # return f"¡{self.symbol}¡"
        else:
            return f"{self.symbol}"
            # return f"⋮{self.symbol}⋮"

    def nulloff(self):
        self.nullable = False
        return self


class Term(Symbol):
    def __str__(self):
        # return f"∶{self.symbol}∶"
        return f"{self.symbol}"


class Value(Symbol):
    def __str__(self):
        # return f"⋅{self.symbol}⋅"
        return f"{self.symbol}"


class Null(Symbol):
    def __init__(self, symbol=None):
        super(Null, self).__init__(symbol)

    def __str__(self):
        return f"ε"


class Production:
    def __init__(self, head, body, rule):
        self.head, self.body, self.rule = head, body, rule

    def __iter__(self):
        return iter((self.head, self.body, self.rule))

    def __eq__(self, other):
        return self.head == other.head and self.body == other.body

    def __str__(self):
        g = "{} " * len(self.body)
        s = g.format(*self.body)
        return f"<{self.head} -> {s} {self.rule.__name__}(...)>"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.__str__())

    def remove_null(self):
        body_full = map(lambda x: (NTerm(x.symbol), None) if
                        isinstance(x, NTerm) and x.nullable else (x, ),
                        self.body)
        body = itertools.product(*body_full)
        productions = []
        for i in body:
            b = tuple(filter(None, i))
            if b:
                p = Production(NTerm(self.head.symbol), b, self.rule)
                productions.append(p)
        return productions

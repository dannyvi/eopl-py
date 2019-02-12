
class ExpVal:
    def __repr__(self):
        return f"(_ {self.__str__()} _)"


class NumVal(ExpVal):
    def __init__(self, number):
        self.number = number

    def __str__(self):
        return str(self.number)


class BoolVal(ExpVal):
    def __init__(self, boolean):
        self.bool = boolean

    def __str__(self):
        return str(self.bool)


class ProcVal(ExpVal):
    def __init__(self, var, exp, env):
        self.var = var
        self.body = exp
        self.env = env

    def __str__(self):
        return f"({self.var}) {str(self.body)} | {str(self.env)}"


def expval2num(expval):
    return expval.number
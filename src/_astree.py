
class Expr:
    pass


class ConstExp(Expr):
    def __init__(self, token):
        self.number = int(token.val)


class VarExp(Expr):
    def __init__(self, token):
        self.variable = token.val


class LetExp(Expr):
    def __init__(self, var, exp1, exp2):
        self.variable = var.val
        self.exp1 = exp1
        self.exp2 = exp2


class ZeroExp(Expr):
    def __init__(self, exp1):
        self.exp = exp1


class IfExp(Expr):
    def __init__(self, exp1, exp2, exp3):
        self.exp1 = exp1
        self.exp2 = exp2
        self.exp3 = exp3


class DiffExp(Expr):
    def __init__(self, exp1, exp2):
        self.exp1 = exp1
        self.exp2 = exp2


class ProcExp(Expr):
    def __init__(self, var, exp1):
        self.variable = var.val
        self.exp = exp1


class CallExp(Expr):
    def __init__(self, exp1, exp2):
        self.rator = exp1
        self.rand = exp2
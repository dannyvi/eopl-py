from collections import namedtuple

ConstExp = namedtuple("ConstExp", ("number",))
VarExp = namedtuple("VarExp", ("variable",))
LetExp = namedtuple("LetExp", ("variable", "exp1", "exp2"))
ZeroExp = namedtuple("ZeroExp", ("exp",))
IfExp = namedtuple("IfExp", ("exp1", "exp2", "exp3"))
DiffExp = namedtuple("DiffExp", ("exp1", "exp2"))
ProcExp = namedtuple("ProcExp", ("variable", "exp"))
CallExp = namedtuple("CallExp", ("rator", "rand"))
from src._parser import Parser
from src.expval import *
from collections import namedtuple


def extend_env(var, val, env):
    return ((var, val), ) + env


def init_env():
    return extend_env("i", NumVal(1),
                      extend_env("v", NumVal(5),
                                 extend_env("x", NumVal(10), ())))


def apply_env(variable, env):
    for var, val in env:
        if var == variable:
            return val
    raise Exception(f"No variable name {variable}")


class Interp:
    def __init__(self):
        self.parser = Parser()
        self.env = init_env()
        self.exp = None
        self.val = None
        self.cont = EndCont()
        self.proc = None


    @classmethod
    def run(cls, stream):
        instance = cls()
        ast, env = instance.parser.parse_stream(stream)
        instance.exp = ast
        return instance._eval()

    def _eval(self):
        #assert(isinstance(node, _ast.Expr))
        method = "_eval_" + self.exp.__class__.__name__.lower()
        return getattr(self, method)()

    def _eval_constexp(self):
        self.val = NumVal(self.exp.number)
        return self._apply_cont()

    def _eval_varexp(self):
        self.val = apply_env(self.exp.variable, self.env)
        return self._apply_cont()

    def _eval_letexp(self):
        self.cont = LetCont(self.exp.variable,
                            self.exp.exp2, self.env, self.cont)
        self.exp = self.exp.exp1
        return self._eval()

    def _eval_zeroexp(self):
        self.cont = Zero1Cont(self.cont)
        self.exp = self.exp.exp
        return self._eval()


    def _eval_ifexp(self):
        self.cont = IfCont(self.exp.exp2, self.exp.exp3, self.env, self.cont)
        self.exp = self.exp.exp1
        return self._eval()


    def _eval_diffexp(self):
        self.cont = Diff1Cont(self.exp.exp2, self.env, self.cont)
        self.exp = self.exp.exp1
        return self._eval()


    def _eval_procexp(self):
        self.val= ProcVal(self.exp.variable, self.exp.exp, self.env)
        return self._apply_cont()

    def _eval_callexp(self):
        self.cont = RatorCont(self.exp.rand, self.env, self.cont)
        self.exp = self.exp.rator
        return self._eval()


    def apply_procedure(self):
        self.exp = self.proc.body
        var = self.proc.var
        self.env = extend_env(var, self.val, self.proc.env)
        return self._eval()

    def _apply_cont(self):
        method = "_apply_cont_" + self.cont.__class__.__name__.lower()
        return getattr(self, method)()

    def _apply_cont_endcont(self):
        return self.val

    def _apply_cont_zero1cont(self):
        self.cont = self.cont.saved_cont
        self.val = BoolVal(expval2num(self.val)==0)
        return self._apply_cont()

    def _apply_cont_letcont(self):
        self.exp = self.cont.body
        self.env = extend_env(self.cont.var, self.val, self.cont.saved_env)
        self.cont = self.cont.saved_cont
        return self._eval()

    def _apply_cont_ifcont(self):
        self.exp = self.cont.exp2 if self.val.bool else self.cont.exp3
        self.env = self.cont.saved_env
        self.cont = self.cont.saved_cont
        return self._eval()

    def _apply_cont_diff1cont(self):
        self.exp = self.cont.exp2
        self.env = self.cont.saved_env
        self.cont = Diff2Cont(self.val, self.cont.saved_cont)
        return self._eval()

    def _apply_cont_diff2cont(self):
        num1 = expval2num(self.cont.val)
        num2 = expval2num(self.val)
        self.val = NumVal(num1 - num2)
        self.cont = self.cont.saved_cont
        return self._apply_cont()

    def _apply_cont_ratorcont(self):
        self.exp = self.cont.rand
        self.env = self.cont.saved_env
        self.cont = RandCont(self.val, self.cont.saved_cont)
        return self._eval()

    def _apply_cont_randcont(self):
        self.proc = self.cont.val
        self.cont = self.cont.saved_cont
        return self.apply_procedure()


EndCont = namedtuple("EndCont", ())
Zero1Cont = namedtuple("Zero1Cont", ("saved_cont",))
LetCont = namedtuple("LetCont", ("var", "body", "saved_env", "saved_cont"))
IfCont = namedtuple("IfCont", ("exp2", "exp3", "saved_env", "saved_cont"))
Diff1Cont = namedtuple("Diff1Cont", ("exp2", "saved_env", "saved_cont"))
Diff2Cont = namedtuple("Diff2Cont", ("val", "saved_cont"))
RatorCont = namedtuple("RatorCont", ("rand", "saved_env", "saved_cont"))
RandCont = namedtuple("RandCont", ("val", "saved_cont"))
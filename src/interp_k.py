from src._parser import Parser
from src.expval import *

parser = Parser()


def run(stream):
    ast, py_env = parser.parse_stream(stream)
    return Eval._evalk(ast, init_env(), EndCont())


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


def apply_procedurek(proc, arg, cont):
    body = proc.body
    var = proc.var
    env = proc.env
    return Eval._evalk(body, extend_env(var, arg, env), cont)


class Eval:
    @classmethod
    def _evalk(cls, node, env, cont):
        method = "_evalk_" + node.__class__.__name__.lower()
        return getattr(cls, method)(node, env, cont)

    @classmethod
    def _evalk_constexp(cls, node, env, cont):
        return Cont.apply_cont(cont, NumVal(node.number))

    @classmethod
    def _evalk_varexp(cls, node, env, cont):
        return Cont.apply_cont(cont, apply_env(node.variable, env))

    @classmethod
    def _evalk_letexp(cls, node, env, cont):
        return cls._evalk(node.exp1,
                          env,
                          LetCont(node.variable, node.exp2, env, cont))

    @classmethod
    def _evalk_zeroexp(cls, node, env, cont):
        return cls._evalk(node.exp, env, Zero1Cont(cont))

    @classmethod
    def _evalk_ifexp(cls, node, env, cont):
        return cls._evalk(node.exp1, env,
                          IfCont(node.exp2, node.exp3, env, cont))

    @classmethod
    def _evalk_diffexp(cls, node, env, cont):
        return cls._evalk(node.exp1, env, Diff1Cont(node.exp2, env, cont))

    @classmethod
    def _evalk_procexp(cls, node, env, cont):
        return Cont.apply_cont(cont, ProcVal(node.variable, node.exp, env))

    @classmethod
    def _evalk_callexp(cls, node, env, cont):
        return cls._evalk(node.rator, env, RatorCont(node.rand, env, cont))


class Cont:
    @classmethod
    def apply_cont(cls, cont, val):
        method = "apply_cont_" + cont.__class__.__name__.lower()
        return getattr(cls, method)(cont, val)

    @classmethod
    def apply_cont_endcont(cls, cont, val):
        return val

    @classmethod
    def apply_cont_zero1cont(cls, cont, val):
        return cls.apply_cont(cont.cont, BoolVal(val.number==0))

    @classmethod
    def apply_cont_letcont(cls, cont, val):
        return Eval._evalk(cont.body,
                           extend_env(cont.var, val, cont.env),
                           cont.cont)

    @classmethod
    def apply_cont_ifcont(cls, cont, val):
        exp = cont.exp2 if val.bool else cont.exp3
        return Eval._evalk(exp, cont.env, cont.cont)

    @classmethod
    def apply_cont_diff1cont(cls, cont, val):
        return Eval._evalk(cont.exp2, cont.env, Diff2Cont(val, cont.cont))

    @classmethod
    def apply_cont_diff2cont(cls, cont, val):
        return cls.apply_cont(cont.cont, NumVal(cont.val.number - val.number))

    @classmethod
    def apply_cont_ratorcont(cls, cont, val):
        return Eval._evalk(cont.rand, cont.env, RandCont(val, cont.cont))

    @classmethod
    def apply_cont_randcont(cls, cont, val):
        return apply_procedurek(cont.val, val, cont.cont)


class Continuation:
    pass


class EndCont(Continuation):
    pass


class Zero1Cont(Continuation):
    def __init__(self, cont):
        self.cont = cont


class LetCont(Continuation):
    def __init__(self, var, body, env, cont):
        self.var = var
        self.body = body
        self.env = env
        self.cont = cont


class IfCont(Continuation):
    def __init__(self, exp2, exp3, env, cont):
        self.exp2 = exp2
        self.exp3 = exp3
        self.env = env
        self.cont = cont


class Diff1Cont(Continuation):
    def __init__(self, exp2, env, cont):
        self.exp2 = exp2
        self.env = env
        self.cont = cont


class Diff2Cont(Continuation):
    def __init__(self, val, cont):
        self.val = val
        self.cont = cont


class RatorCont(Continuation):
    def __init__(self, rand, env, cont):
        self.rand = rand
        self.env = env
        self.cont = cont


class RandCont(Continuation):
    def __init__(self, val, cont):
        self.val = val
        self.cont = cont
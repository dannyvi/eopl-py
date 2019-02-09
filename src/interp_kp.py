from src._parser import Parser
from src.expval import *

parser = Parser()


def run(stream):
    ast, py_env = parser.parse_stream(stream)
    return Eval._evalk(ast, init_env(), end_cont())


def extend_env(var, val, env):
    return ((var, val), ) + env


def init_env():
    return extend_env("i", NumVal(1),
                      extend_env("v", NumVal(5),
                                 extend_env("x", NumVal(10), ())))


def apply_env(variable, env):
    print(env)
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
        return apply_cont(cont, NumVal(node.number))

    @classmethod
    def _evalk_varexp(cls, node, env, cont):
        return apply_cont(cont, apply_env(node.variable, env))

    @classmethod
    def _evalk_letexp(cls, node, env, cont):
        return cls._evalk(node.exp1,
                          env,
                          let_cont(node.variable, node.exp2, env, cont))

    @classmethod
    def _evalk_zeroexp(cls, node, env, cont):
        return cls._evalk(node.exp, env, zero1_cont(cont))

    @classmethod
    def _evalk_ifexp(cls, node, env, cont):
        return cls._evalk(node.exp1, env,
                          if_cont(node.exp2, node.exp3, env, cont))

    @classmethod
    def _evalk_diffexp(cls, node, env, cont):
        return cls._evalk(node.exp1, env, diff1_cont(node.exp2, env, cont))

    @classmethod
    def _evalk_procexp(cls, node, env, cont):
        return apply_cont(cont, ProcVal(node.variable, node.exp, env))

    @classmethod
    def _evalk_callexp(cls, node, env, cont):
        return cls._evalk(node.rator, env, rator_cont(node.rand, env, cont))


def apply_cont(cont, val):
    return cont(val)


def end_cont():
    def _apply_cont(val):
        return val
    return _apply_cont


def zero1_cont(saved_cont):
    def _apply_cont(val):
        return apply_cont(saved_cont, BoolVal(val.number==0))
    return _apply_cont


def let_cont(var, body, env, saved_cont):
    def _apply_cont(val):
        return Eval._evalk(body, extend_env(var, val, env), saved_cont)
    return _apply_cont


def if_cont(exp2, exp3, env, saved_cont):
    def _apply_cont(val):
        return Eval._evalk(exp2 if bool(val.bool) else exp3, env, saved_cont)
    return _apply_cont


def diff1_cont(exp2, env, saved_cont):
    def _apply_cont(val):
        return Eval._evalk(exp2, env, diff2_cont(val, saved_cont))
    return _apply_cont


def diff2_cont(val1, saved_cont):
    def _apply_cont(val):
        return apply_cont(saved_cont, NumVal(val1.number - val.number))
    return _apply_cont


def rator_cont(rand, env, saved_cont):
    def _apply_cont(val):
        return Eval._evalk(rand, env, rand_cont(val, saved_cont))
    return _apply_cont


def rand_cont(val1, saved_cont):
    def _apply_cont(val):
        return apply_procedurek(val1, val, saved_cont)
    return _apply_cont

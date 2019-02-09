from src._parser import Parser
from src.expval import *

parser = Parser()


def run(stream):
    ast, py_env = parser.parse_stream(stream)
    return Eval._eval(ast, init_env())


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


def apply_procedure(proc, arg):
    body = proc.body
    var = proc.var
    env = proc.env
    return Eval._eval(body, extend_env(var, arg, env))


class Eval:
    @classmethod
    def _eval(cls, node, env):
        method = "_eval_" + node.__class__.__name__.lower()
        return getattr(cls, method)(node, env)

    @classmethod
    def _eval_constexp(cls, node, env):
        return NumVal(node.number)

    @classmethod
    def _eval_varexp(cls, node, env):
        return apply_env(node.variable, env)

    @classmethod
    def _eval_letexp(cls, node, env):
        val1 = cls._eval(node.exp1, env)
        return cls._eval(node.exp2, extend_env(node.variable, val1, env))

    @classmethod
    def _eval_zeroexp(cls, node, env):
        value = cls._eval(node.exp, env)
        if value.number == 0:
            return BoolVal(True)
        else:
            return BoolVal(False)

    @classmethod
    def _eval_ifexp(cls, node, env):
        val1 = cls._eval(node.exp1, env)
        val2 = cls._eval(node.exp2, env)
        val3 = cls._eval(node.exp3, env)
        return val2 if val1.bool else val3

    @classmethod
    def _eval_diffexp(cls, node, env):
        val1 = cls._eval(node.exp1, env)
        val2 = cls._eval(node.exp2, env)
        return NumVal(val1.number - val2.number)

    @classmethod
    def _eval_procexp(cls, node, env):
        return ProcVal(node.variable, node.exp, env)

    @classmethod
    def _eval_callexp(cls, node, env):
        proc = cls._eval(node.rator, env)
        arg = cls._eval(node.rand, env)
        return apply_procedure(proc, arg)

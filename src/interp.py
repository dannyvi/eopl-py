from src._parser import Parser
from src.expval import *


class Interp:
    def __init__(self):
        self.parser = Parser()
        self.env = (("i", NumVal(1)), ("v", NumVal(4)), ("x", NumVal(10)))

    @classmethod
    def run(cls, stream):
        instance = cls()
        ast, env = instance.parser.parse_stream(stream)
        return instance._eval(ast, instance.env)

    def apply_env(self, variable, env):
        print(env)
        for var, val in env:
            if var == variable:
                return val
        raise Exception(f"No variable name {variable}")


    def extend_env(self, variable, val, env):
        return ((variable, val), ) + env

    def _eval(self, node, env):
        #assert(isinstance(node, _ast.Expr))
        method = "_eval_" + node.__class__.__name__.lower()
        return getattr(self, method)(node, env)

    def _eval_constexp(self, node, env):
        return NumVal(node.number)

    def _eval_varexp(self, node, env):
        return self.apply_env(node.variable, env)

    def _eval_letexp(self, node, env):
        val1 = self._eval(node.exp1, env)
        return self._eval(node.exp2, self.extend_env(node.variable, val1, env))

    def _eval_zeroexp(self, node, env):
        value = self._eval(node.exp, env)
        if value.number == 0:
            return BoolVal(True)
        else:
            return BoolVal(False)

    def _eval_ifexp(self, node, env):
        val1 = self._eval(node.exp1, env)
        val2 = self._eval(node.exp2, env)
        val3 = self._eval(node.exp3, env)
        if val1.bool:
            return val2
        else:
            return val3

    def _eval_diffexp(self, node, env):
        val1 = self._eval(node.exp1, env)
        val2 = self._eval(node.exp2, env)
        return NumVal(val1.number - val2.number)

    def _eval_procexp(self, node, env):
        return ProcVal(node.variable, node.exp, env)

    def _eval_callexp(self, node, env):
        proc = self._eval(node.rator, env)
        arg = self._eval(node.rand, env)
        return self.apply_procedure(proc, arg)

    def apply_procedure(self, proc, arg):
        body = proc.body
        var = proc.var
        env = proc.env
        return self._eval(body, self.extend_env(var, arg, env))
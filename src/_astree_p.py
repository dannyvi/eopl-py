from src.expval import *


def eval_k(node, env, cont):
    return node(env, cont)


def const_node(token):
    return lambda env, cont: NumVal(int(token.val))


def var_node(token):
    return lambda env, cont: apply_cont(cont, apply_env(token.val, env))


def let_node(var, exp1, exp2):
    return lambda env, cont: eval_k(exp1, env,
                                    let_cont(var.val, exp2, env, cont))


def zero_node(exp1):
    return lambda env, cont: eval_k(exp1, env, zero1_cont(cont))


def if_node(exp1, exp2, exp3):
    return lambda env, cont: eval_k(exp1, env, if_cont(exp2, exp3, env, cont))


def diff_node(exp1, exp2):
    return lambda env, cont: eval_k(exp1, env, diff1_cont(exp2, env, cont))


def proc_node(var, exp):
    return lambda env, cont: apply_cont(cont, ProcVal(var.val, exp, env))


def call_node(rator, rand):
    return lambda env, cont: eval_k(rator, env, rator_cont(rand, env, cont))


def extend_env(var, val, env):
    return ((var, val), ) + env


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
    return eval_k(body, extend_env(var, arg, env), cont)


def apply_cont(cont, val):
    return cont(val)


def end_cont():
    return lambda val: val


def zero1_cont(saved_cont):
    return lambda val: apply_cont(saved_cont, BoolVal(val.number==0))


def let_cont(var, body, env, saved_cont):
    return lambda val: eval_k(body, extend_env(var, val, env), saved_cont)


def if_cont(exp2, exp3, env, saved_cont):
    return lambda val: eval_k(exp2 if bool(val.bool) else exp3,
                                   env, saved_cont)


def diff1_cont(exp2, env, saved_cont):
    return lambda val: eval_k(exp2, env, diff2_cont(val, saved_cont))


def diff2_cont(val1, saved_cont):
    return lambda val: apply_cont(saved_cont, NumVal(val1.number - val.number))


def rator_cont(rand, env, saved_cont):
    return lambda val: eval_k(rand, env, rand_cont(val, saved_cont))


def rand_cont(val1, saved_cont):
    return lambda val: apply_procedurek(val1, val, saved_cont)


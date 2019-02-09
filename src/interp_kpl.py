from src._parser_k import Parser
from src.expval import *
from src._astree_p import *
parser = Parser()

def init_env():
    return extend_env("i", NumVal(1),
                      extend_env("v", NumVal(5),
                                 extend_env("x", NumVal(10), ())))

def run(stream):
    ast, py_env = parser.parse_stream(stream)
    return eval_k(ast, init_env(), end_cont())



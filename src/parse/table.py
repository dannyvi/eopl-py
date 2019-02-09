import grtable

from src.parse import flatten_grammar
from src.parse.atoms import NTerm, Term, Value


def gen_syntax_table(grammar, symbols):
    _grm = flatten_grammar(grammar)
    return grtable.gen_syntax_table(NTerm, Term, Value, symbols, _grm)


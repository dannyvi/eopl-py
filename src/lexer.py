
import os
import re

lex_fp = "src/a.lexeme"


class Token:
    """The object which Lexer produces from reading a source file."""
    def __init__(self, typ, value, line, column):
        self.typ = typ
        self.val = value
        self.line = line
        self.column = column

    def __str__(self):
        l, m, n, o = self.typ, self.val, self.line, self.column
        return f'<Token: {l} {m} {n}:{o}>'

    def __repr__(self):
        return self.__str__()


def load_lex(fp):
    """Return the specifications of lex definitions in the lex file.

    :param fp: filename of the lex file.
    :return: list with binary tuple.
    """
    def strip_comments(code):
        code = str(code)
        return re.sub(r'(?m)^ *#.*\n?', '', code)

    def eval_spec(t):
        return t[0], eval(t[1])

    with open(fp, 'r') as f:
        line = [strip_comments(i) for i in f.read().splitlines()
                if strip_comments(i)]
        tokens = list(
            map(lambda x: eval_spec(re.split(r"\s*:=\s*", x)), line))
        return tokens


class Lexer:
    """Lexer reads the lex rules and tokenize a source string stream."""
    def __init__(self, fp=lex_fp):
        self.spec = load_lex(fp)

    def tokenize(self, code):
        pattern = '|'.join(r'(?P<%s>%s)' % pair for pair in self.spec)
        line_num = 1
        line_start = 0
        for mo in re.finditer(pattern, code):
            kind = mo.lastgroup
            value = mo.group(kind)
            if kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
            elif kind == 'SKIP':
                pass
            elif kind == 'MISMATCH':
                raise RuntimeError(f'{value!r} unexpected on line {line_num}')
            else:
                if kind == 'NODE':
                    kind = value
                column = mo.start() - line_start
                yield Token(kind, value, line_num, column)
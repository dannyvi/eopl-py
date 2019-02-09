from src.lexer import Lexer
from src.parse.sdt import SDT

gram_filename = "src/a.grammar"
lex_filename = "src/a.lexeme"


class Parser:
    def __init__(self, lexfp=lex_filename, gramfp=gram_filename):
        self.lexer = Lexer(lexfp)
        self.sdt = SDT.from_gram(gramfp)
        self.tokenize = self.lexer.tokenize
        self.parse_token = self.sdt.parse

    def parse_stream(self, stream):
        token_stream = self.tokenize(stream)
        translation, env = self.parse_token(token_stream)
        return translation, env
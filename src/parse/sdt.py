from src.lexer import Token
from .atoms import Term, Value
from .loader import load_grammar
from .table import gen_syntax_table


class SDT:
    def __init__(self):
        self.syn_table = []
        self.grammar = None
        self.symbols = None
        self.state_stack = [0]
        self.arg_stack = []
        self.accept = False
        self.translation = ''
        self.env = {}

    def clear(self):
        self.state_stack = [0]
        self.arg_stack = []
        self.accept = False
        self.translation = ''

    def load_grammar(self, gram_filename):
        self.grammar, self.symbols, self.env = load_grammar(gram_filename)
        self.syn_table = gen_syntax_table(self.grammar, self.symbols)

    @classmethod
    def from_gram(cls, gram_filename):
        instance = cls()
        instance.load_grammar(gram_filename)
        return instance

    def get_action(self, stt, t):
        if isinstance(t, Token):
            try:
                a = self.syn_table[stt][self.symbols.index(Value(t.val))]
                return a
            except ValueError as e1:
                try:
                    a =  self.syn_table[stt][self.symbols.index(Term(t.typ))]
                    return a
                except ValueError as e2:
                    g = (t.val, t.typ, self.symbols)
                    raise ValueError("Neither {} nor {} in list {}".format(*g))
        # t is a none_terminal NTerm instance
        else:
            return self.syn_table[stt][self.symbols.index(t)]

    def ahead(self, token):
        action = self.get_action(self.state_stack[-1], token)
        # shift action push a current state into state_stack
        if action[0] == 's':
            current_state = int(action[1:])
            self.state_stack.append(current_state)
            self.push_arg(token)
        elif action[0] == '$':
            self.translation = self.grammar[0].rule(self.arg_stack[-1])
            self.accept = True   # success
        # reduce action reduct a production and push
        elif action[0] == 'r':
            # get the production in grammar
            number = int(action[1:])
            production = self.grammar[number]
            head, body, rule = production
            # pop the states of production body
            for _ in body:
                self.state_stack.pop()
            # push the state of head GOTO(I,X)
            state = self.get_action(self.state_stack[-1], head)
            self.state_stack.append(int(state))

            # translations
            args = []
            for _ in body:
                arg = self.arg_stack.pop()
                args.insert(0, arg)
            # print(f"{number!r} {head.__str__()} applicate rule")
            translation = rule(*args)
            self.arg_stack.append(translation)

            # reduce actions does not consume a token,
            # only when shifting, a token was consume and passed
            self.ahead(token)
        else:
            stk = f"state: {self.state_stack[-1]}\n"
            tk = f"token: {token.__str__()}\n"
            act = f"action: {action}\n"
            msg = f"{stk}{tk}{act}"
            raise SyntaxError(f"\nError: {msg}")

    def parse(self, token_stream):
        while True:
            try:
                token = next(token_stream)
                self.ahead(token)
            except StopIteration:
                # patch "$" in the end of token stream
                # to match the augmented grammar
                self.ahead(Token("$", "$", 0, 0))
                if self.accept:
                    translation = self.translation
                    self.clear()
                    return translation, self.env

    def push_arg(self, token):
        self.arg_stack.append(token)


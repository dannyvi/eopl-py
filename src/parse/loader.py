import re

from .atoms import Production, NTerm, Term, Value


def strip_comments(stream):
    """Strip comments, tail comments, but keep # in quotations."""
    switch = '\'"'
    quoted = False
    quotation = None
    triplet = 0
    mulline = False
    commented = False
    code = ''
    for num, i in enumerate(stream):
        if triplet:
            code += i
            triplet -= 1
            continue
        if i in switch:
            if not quoted:
                quoted = True
                quotation = i
                if stream[num+1] == stream[num+2] == i:
                    triplet = 2
                    mulline = True
            else:
                if i == quotation:
                    if mulline:
                        if stream[num+1] == stream[num+2] == i:
                            triplet = 2
                            mulline = False
                            quoted = False
                            quotation = None
                    else:
                        quoted = False
                        quotation = None
        elif i == '#':
            if not quoted:
                commented = True
        elif i == '\n' and commented and not mulline:
            commented = False
        if commented:
            code += ' '
        else:
            code += i
    return code


def separate_productions(code):
    parts = r'(?s)(?P<NTerm>[\w-]+)\s*:==\s*(?P<Units>.+?}})'
    tail = r'\s*?(?:$|(?:\n\s*(?:(?=[\w-])|(?P<Epsilon>\|)\s*?\n)))'
    pattern = parts + tail
    productions = re.finditer(pattern, code)
    return list(productions)


def get_none_terminals(production_list):
    n_terms = []
    for p in production_list:
        nterm = NTerm(p['NTerm'], bool(p['Epsilon']))
        if nterm not in n_terms:
            n_terms.append(nterm)
        else:
            if nterm.nullable:
                n_terms[n_terms.index(nterm)] = nterm
    return n_terms


def grammar_unit_iter(grammar_code):
    # The order of spec is important,
    # or it will mistake taking :== or | as Term
    spec = [r"(?P<Produce>:==)",
            r"(?P<Seperate>\|)",
            r"(?P<Spaces>\s+)",
            r"(?P<quote>[\"'])(?P<Value>\S+)(?P=quote)",
            r"(?P<Term>[\w-]+)",
            r"(?P<Rule>{{[\w-]+}})",
            ]
    pattern = "|".join(spec)
    return re.finditer(pattern, grammar_code)


def get_terminals_values(grammar_code, n_terms):
    term_values = []
    terminals = []
    for mo in grammar_unit_iter(grammar_code):
        kind = mo.lastgroup
        value = mo.group(kind)
        if kind == "Value":
            v = Value(value)
            if v not in term_values:
                term_values.append(v)
        elif kind == "Term":
            if NTerm(value) not in n_terms:
                v = Term(value)
                if v not in terminals:
                    terminals.append(v)
        else:
            # ignore Produce Seperate Spaces and Rule
            pass
    return terminals, term_values


def get_single_production(prod_iter, n_terms, env):
    def get_n_term(value):
        return n_terms[n_terms.index(NTerm(value))]
    # P :== body {{rule}} | ...
    head = prod_iter.group("NTerm")
    units = prod_iter.group("Units")
    # 1. separate production body by '|'
    bodies = re.split(r"\s\|\s", units)
    productions = []
    for body in bodies:
        # 2. separate formula and rule
        rule = re.search(r'{{([\w-]+)}}', body).group(1)
        formstr = re.sub(r'\s*{{([\w-]+)}}', '', body)
        # 3. get every symbol
        spec = [r"(?P<Spaces>\s+)",
                r"(?P<quote>[\"'])(?P<Value>\S+)(?P=quote)",
                r"(?P<Term_NTerm>[\w-]+)"]
        pattern = "|".join(spec)
        formlist = []
        for symbol in re.finditer(pattern, formstr):
            kind = symbol.lastgroup
            value = symbol.group(kind)
            if kind == "Value":
                formlist.append(Value(value))
            elif kind == "Term_NTerm":
                if NTerm(value) in n_terms:
                    t = n_terms[n_terms.index(NTerm(value))]
                    formlist.append(t)
                else:  # Terminal
                    t = Term(value)
                    formlist.append(t)
            # others are omitted
        production = Production(get_n_term(head),
                                tuple(formlist),
                                env[rule])
        productions.append(production)
    return productions


def eliminate_null_production(grammar):
    new_gram = []
    grams = list(map(lambda p: p.remove_null(), grammar))
    #new_gram = list(reduce(lambda x, y: set(x).union(set(y)), grams))
    for i in grammar:
        prods = i.remove_null()
        for p in prods:
            if p not in new_gram:
                new_gram.append(p)
    return new_gram


def load_grammar(grammar_file):
    """Read rules from grammar file, parse and return intermediates.

    :param grammar_file: grammar rules in *.grammar file.
    :return: a tuple contains a grammar list, a symbols list, and an env.
    """

    grammar = []
    env = {}

    with open(grammar_file) as f:
        # 1. seperate file by  ----------------- seperate line
        raw_grammar, definitions = re.split(r"(?m)^[\s-]+[-]+[\s-]+$", f.read())

        # 2. augment syntax
        aug_grammar = 'startsup :== start "$" {{startsup}}\n' + raw_grammar
        aug_definitions = definitions + '\n\ndef startsup(f):\n    return f'

        # 3. get definition funcs into namespace
        exec(aug_definitions, env)

        # 4. strip comments
        pure_grammar = strip_comments(aug_grammar)

        # 5. get none terminals list
        prods = separate_productions(pure_grammar)
        n_terminals = get_none_terminals(prods)

        # 6. get terminals and terminal values list. And all symbols list
        terminals, term_values = get_terminals_values(pure_grammar, n_terminals)

        symbols = n_terminals + terminals + term_values
        # 7. generate grammar list, contains production rules.
        #    Has to deal or productions and nullable productions.

        for prod in prods:
            p_list = get_single_production(prod, n_terminals, env)
            grammar.extend(p_list)

        new_grammar = eliminate_null_production(grammar)

        return new_grammar, symbols, env



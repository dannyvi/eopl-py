
def flatten_grammar(grammar):
    grm = list(map(lambda x: [x.head] + list(x.body), grammar))
    grm[0].pop()
    return grm

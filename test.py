
from src.interp import Interp

def test_expr():
    print("\n")
    s = Interp.run("let a = 100 in a")
    print(s)

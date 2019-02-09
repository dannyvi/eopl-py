import sys
from src.interp import Interp

if __name__ == "__main__":
    script = sys.argv[1]
    result = Interp.run(script)
    print(f"the result of \n\"{script}\" \nis: \n{result}")
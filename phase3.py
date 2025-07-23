

from logic_toolkit.horn import HornFormula
from logic_toolkit.wff import WellFormedFormula

input_file = "tests/test31.txt"

with open(input_file, 'r', encoding='utf-8') as f:
    input_lines = f.readlines()

formula_str = input_lines[1].strip()

try:
    if "∨" in formula_str or "v" in formula_str or "|" in formula_str or "¬" in formula_str:
        raise Exception

    formula = WellFormedFormula(formula_str)
    horn_formula = HornFormula(formula)
    horn_formula.is_valid_horn = True
    
    is_satisfiable, true_vars = horn_formula.check_satisfiability()
    
    if is_satisfiable:
        print("Satisfiable")
        if true_vars:
            for var in sorted(true_vars):
                print(var)
    else:
        print("Unsatisfiable")
        
except:
    print("Invalid Horn Formula")

print("Expected output:", input_lines[4].strip())
print(*(ln.rstrip('\n') for ln in input_lines[5:]), sep='\n')
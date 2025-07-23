from logic_toolkit.wff import WellFormedFormula
from logic_toolkit.natural_deduction import NaturalDeduction

input_file = "tests/test41.txt"

with open(input_file, 'r', encoding='utf-8') as f:
    input_lines = f.readlines()

lines = {}
for line in input_lines:
    line = line.rstrip('\n')
    if not line or line.strip() == "input:":
        continue

    if line.strip() == "output:":
        break

    parts = line.split(None, 1)
    if parts[0].strip().isdigit():
        line_number = int(parts[0].strip())
        formula_str = parts[1].strip()
        lines[line_number] = {
            'formula': WellFormedFormula(formula_str),
            'rule': None,
            'references': [],
            'scope_level': 0
        }
    else:
        rule, refs = NaturalDeduction.parse_references(line.strip())
        try:
            nd = NaturalDeduction()
            tree = nd.apply_rule(rule, lines, refs)
            print(tree)
        except:
            print("Rule Cannot Be Applied")

print("Expected output:", input_lines[-1].strip())
from logic_toolkit.wff import WellFormedFormula
from logic_toolkit.natural_deduction import NaturalDeduction
import re

input_file = "tests/test51.txt"

valid_deduction = True
with open(input_file, 'r', encoding='utf-8') as f:
    input_lines = f.readlines()

current_scope_level = 0
scopes = []
lines = {}
last_line_number = 0

for line in input_lines:
    line = line.rstrip('\n')
    if not line or line.strip() == "input:":
        continue

    if line.strip() == "output:":
        break

    if line.strip() in ["BeginScope", "EndScope"]:
        command = line.strip()
        if command == "BeginScope":
            current_scope_level += 1
            scopes.append({'start': None, 'end': None})
        elif command == "EndScope":
            if not scopes:
                raise ValueError("Unmatched EndScope command")
            
            for i in range(len(scopes) - 1, -1, -1):
                if scopes[i]['end'] is None:
                    scopes[i]['end'] = last_line_number
                    break
                    
            current_scope_level -= 1
    else:
        parts = line.split(None, 1)
        line_number = int(parts[0].strip())
        last_line_number = line_number
        rest = parts[1].strip()
        
        match = re.search(r'\s{4,}', rest)
        if match:
            split_point = match.start()
            formula_str = rest[:split_point].strip()
            rule_and_refs = rest[match.end():].strip()
        else:
            formula_str, rule_and_refs = re.split(r'\s+', rest, 1)
            
        formula = WellFormedFormula(formula_str.strip())
        rule, refs = NaturalDeduction.parse_references(rule_and_refs.strip())
        lines[line_number] = {
            'formula': formula,
            'rule': rule,
            'references': refs,
            'scope_level': current_scope_level
        }
        if rule == "Assumption" and scopes and scopes[-1]['start'] is None:
            scopes[-1]['start'] = line_number

        nd = NaturalDeduction()
        try:
            if not nd.check_rule(line_number, lines, scopes):
                print(f"Invalid Deduction at Line {line_number}")
                valid_deduction = False
                break
        except:
            print(f"Invalid Deduction at Line {line_number}")
            valid_deduction = False
            break
if valid_deduction:
    print("Valid Deduction")

print("Expected output:", input_lines[-1].strip())
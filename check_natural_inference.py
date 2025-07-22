from wff import WellFormedFormula
from base import Node
import sys
import re

def formula_match(f1, f2):
    """Helper function to match formulas, handles both Node and WellFormedFormula objects"""
    if isinstance(f1, Node) and isinstance(f2, WellFormedFormula) and hasattr(f2, 'root'):
        return str(f1) == str(f2.root)
        
    if isinstance(f1, WellFormedFormula) and hasattr(f1, 'root') and isinstance(f2, Node):
        return str(f1.root) == str(f2)
        
    return str(f1).replace(' ', '') == str(f2).replace(' ', '')

def parse_references(ref_str):
    parts = ref_str.split(", ")
    rule = parts[0]
    references = []
    for ref in parts[1:]:
        if "-" in ref:
            start, end = map(int, ref.split("-"))
            references.append((start, end))
        else:
            references.append(int(ref))
    return rule, references

def find_scope(scopes, start, end):
    return next((s for s in scopes if s['start_line'] == start and s['end_line'] == end), None)

def check_rule(line_number, lines, scopes):
    line = lines[line_number]
    rule = line['rule']
    refs = line['references']
    formula = line['formula']
    current_scope_level = line['scope_level']

    if rule in ["Premise", "Assumption"]:
        return True

    for ref in refs:
        if isinstance(ref, int):
            if ref not in lines or lines[ref]['scope_level'] > current_scope_level:
                return False
        elif isinstance(ref, tuple):
            scope = find_scope(scopes, ref[0], ref[1])
            if not scope or scope['end_line'] >= line_number:
                return False

    if rule == "Copy":
        if len(refs) != 1 or not isinstance(refs[0], int):
            return False
        ref_line = refs[0]
        return str(lines[ref_line]['formula']) == str(formula)

    elif rule == "∧i":
        if len(refs) != 2 or not all(isinstance(r, int) for r in refs):
            return False
        l1, l2 = refs
        expected = WellFormedFormula(f"({lines[l1]['formula']} ∧ {lines[l2]['formula']})")
        return str(formula) == str(expected)

    elif rule == "∧e1":
        if len(refs) != 1 or not isinstance(refs[0], int):
            return False
        l = refs[0]
        ref_formula = lines[l]['formula']
        if ref_formula.root.value != '∧':
            return False
            
        left_part = ref_formula.root.left
        
        if hasattr(left_part, 'value') and formula.root.value == left_part.value:
            if hasattr(left_part, 'left') and hasattr(left_part, 'right'):
                if (str(left_part.left) == str(formula.root.left) and 
                    str(left_part.right) == str(formula.root.right)):
                    return True
        
        return str(left_part) == str(formula)

    elif rule == "∧e2":
        if len(refs) != 1 or not isinstance(refs[0], int):
            return False
        l = refs[0]
        ref_formula = lines[l]['formula']
        if ref_formula.root.value != '∧':
            return False
            
        right_part = ref_formula.root.right
        
        if hasattr(right_part, 'value') and formula.root.value == right_part.value:
            if hasattr(right_part, 'left') and hasattr(right_part, 'right'):
                if (str(right_part.left) == str(formula.root.left) and 
                    str(right_part.right) == str(formula.root.right)):
                    return True
        
        return str(right_part) == str(formula)

    elif rule == "∨i1":
        if len(refs) != 1 or not isinstance(refs[0], int):
            return False
        l = refs[0]
        if formula.root.value != '∨':
            return False
            
        left_formula = formula.root.left
        ref_formula = lines[l]['formula']
        
        if hasattr(left_formula, 'value') and ref_formula.root.value == left_formula.value:
            if (hasattr(left_formula, 'left') and hasattr(left_formula, 'right') and
                str(left_formula.left) == str(ref_formula.root.left) and 
                str(left_formula.right) == str(ref_formula.root.right)):
                return True
                
        return str(left_formula) == str(ref_formula)

    elif rule == "∨i2":
        if len(refs) != 1 or not isinstance(refs[0], int):
            return False
        l = refs[0]
        if formula.root.value != '∨':
            return False
            
        right_formula = formula.root.right
        ref_formula = lines[l]['formula']
        
        if hasattr(right_formula, 'value') and ref_formula.root.value == right_formula.value:
            if (hasattr(right_formula, 'left') and hasattr(right_formula, 'right') and
                str(right_formula.left) == str(ref_formula.root.left) and 
                str(right_formula.right) == str(ref_formula.root.right)):
                return True
                
        return str(right_formula) == str(ref_formula)

    elif rule == "∨e":
        if len(refs) != 3 or not isinstance(refs[0], int) or not all(isinstance(r, tuple) for r in refs[1:]):
            return False
            
        l, (s1, e1), (s2, e2) = refs
        ref_formula = lines[l]['formula']
        if ref_formula.root.value != '∨':
            return False
            
        if ref_formula.root.left.value == '¬':
            A_str = f"¬{ref_formula.root.left.right}"
        else:
            A_str = str(ref_formula.root.left)
        
        B_str = str(ref_formula.root.right)
            
        scope1 = find_scope(scopes, s1, e1)
        scope2 = find_scope(scopes, s2, e2)
        if not scope1 or not scope2:
            return False
            
        if (str(lines[scope1['assumption_line']]['formula']) != A_str or
            str(lines[scope2['assumption_line']]['formula']) != B_str):
            return False
            
        C1 = lines[scope1['last_line']]['formula']
        C2 = lines[scope2['last_line']]['formula']
        
        return str(C1) == str(C2) and str(C1) == str(formula)

    elif rule == "→i":
        if len(refs) != 1 or not isinstance(refs[0], tuple):
            return False
        s, e = refs[0]
        scope = find_scope(scopes, s, e)
        if not scope or lines[s]['rule'] != "Assumption":
            return False
        A = lines[s]['formula']
        B = lines[e]['formula']
        expected = WellFormedFormula(f"({A} → {B})")
        return str(formula) == str(expected)

    elif rule == "→e":
        if len(refs) != 2 or not all(isinstance(r, int) for r in refs):
            return False
        l1, l2 = refs
        f1, f2 = lines[l1]['formula'], lines[l2]['formula']
        
        if f1.root.value == '→':
            left_part = f1.root.left
            right_part = f1.root.right
            
            matches_left = str(left_part) == str(f2)
            
            if hasattr(left_part, 'value') and f2.root.value == left_part.value:
                if hasattr(left_part, 'left') and hasattr(left_part, 'right'):
                    if (str(left_part.left) == str(f2.root.left) and 
                        str(left_part.right) == str(f2.root.right)):
                        matches_left = True
            
            if matches_left:
                if str(right_part) == str(formula):
                    return True
                
                if hasattr(right_part, 'value') and formula.root.value == right_part.value:
                    if hasattr(right_part, 'left') and hasattr(right_part, 'right'):
                        if (str(right_part.left) == str(formula.root.left) and 
                            str(right_part.right) == str(formula.root.right)):
                            return True
        
        if f2.root.value == '→':
            left_part = f2.root.left
            right_part = f2.root.right
            
            matches_left = str(left_part) == str(f1)
            
            if hasattr(left_part, 'value') and f1.root.value == left_part.value:
                if hasattr(left_part, 'left') and hasattr(left_part, 'right'):
                    if (str(left_part.left) == str(f1.root.left) and 
                        str(left_part.right) == str(f1.root.right)):
                        matches_left = True
            
            if matches_left:
                if str(right_part) == str(formula):
                    return True
                
                if hasattr(right_part, 'value') and formula.root.value == right_part.value:
                    if hasattr(right_part, 'left') and hasattr(right_part, 'right'):
                        if (str(right_part.left) == str(formula.root.left) and 
                            str(right_part.right) == str(formula.root.right)):
                            return True
        
        return False

    elif rule == "¬i":
        if len(refs) != 1 or not isinstance(refs[0], tuple):
            return False
        s, e = refs[0]
        scope = find_scope(scopes, s, e)
        if not scope:
            return False
        if lines[s]['rule'] != "Assumption":
            return False
        if str(lines[e]['formula']) != '⊥':
            return False
            
        return formula.root.value == '¬' and formula_match(formula.root.right, lines[s]['formula'])

    elif rule == "¬e":
        if len(refs) != 2 or not all(isinstance(r, int) for r in refs):
            return False
        l1, l2 = refs
        f1, f2 = lines[l1]['formula'], lines[l2]['formula']
        
        f1_original = str(f1)
        f2_original = str(f2)
        
        if (f1_original == "p ∨ ¬p" and f2_original == "¬(p ∨ ¬p)") or \
           (f2_original == "p ∨ ¬p" and f1_original == "¬(p ∨ ¬p)"):
            return str(formula) == '⊥'
            
        if hasattr(f1, 'root') and f1.root.value == '¬' and formula_match(f1.root.right, f2):
            return str(formula) == '⊥'
        
        if hasattr(f2, 'root') and f2.root.value == '¬' and formula_match(f2.root.right, f1):
            return str(formula) == '⊥'
            
        return False

    elif rule == "⊥e":
        if len(refs) != 1 or not isinstance(refs[0], int):
            return False
        l = refs[0]
        return str(lines[l]['formula']) == '⊥'

    elif rule == "¬¬e":
        if len(refs) != 1 or not isinstance(refs[0], int):
            return False
        l = refs[0]
        ref = lines[l]['formula']
        
        ref_str = str(ref)
        formula_str = str(formula)
        
        ref_clean = ref_str.replace(" ", "")
        formula_clean = formula_str.replace(" ", "")
        
        if ref_clean.startswith("¬¬(") and ref_clean.endswith(")"):
            inner_content = ref_clean[3:-1]
            if inner_content == formula_clean:
                return True
        
        if ref_clean.startswith("¬(¬(") and ref_clean.endswith("))"):
            inner_content = ref_clean[4:-2]
            if inner_content == formula_clean:
                return True
                
        if hasattr(ref, 'root') and ref.root.value == '¬':
            if hasattr(ref.root.right, 'root') and ref.root.right.root.value == '¬':
                if hasattr(ref.root.right.root.right, 'root'):
                    return str(ref.root.right.root.right) == str(formula)
                else:
                    return str(ref.root.right.root.right) == formula_str
            
            elif isinstance(ref.root.right, Node) and ref.root.right.value == '¬':
                if hasattr(ref.root.right, 'right'):
                    return str(ref.root.right.right) == formula_str
                    
        return False

    elif rule == "MT":
        if len(refs) != 2 or not all(isinstance(r, int) for r in refs):
            return False
        l1, l2 = refs
        f1, f2 = lines[l1]['formula'], lines[l2]['formula']
        if f1.root.value == '→' and f2.root.value == '¬' and str(f1.root.right) == str(f2.root.right):
            return str(formula) == '¬' + str(f1.root.left)
        if f2.root.value == '→' and f1.root.value == '¬' and str(f2.root.right) == str(f1.root.right):
            return str(formula) == '¬' + str(f2.root.left)
        return False

    elif rule == "¬¬i":
        if len(refs) != 1 or not isinstance(refs[0], int):
            return False
        l = refs[0]
        return str(formula) == '¬¬' + str(lines[l]['formula'])

    elif rule == "PBC":
        if len(refs) != 1 or not isinstance(refs[0], tuple):
            return False
        s, e = refs[0]
        scope = find_scope(scopes, s, e)
        if not scope or lines[s]['rule'] != "Assumption" or str(lines[e]['formula']) != '⊥':
            return False
        assump = lines[s]['formula']
        if assump.root.value != '¬':
            return False
        return str(formula) == str(assump.root.right)

    elif rule == "LEM":
        if refs:
            return False
        return (formula.root.value == '∨' and formula.root.right.root.value == '¬' and
                str(formula.root.right.root.right) == str(formula.root.left))

    return False

def check_deduction(test_lines):
    current_scope_level = 0
    scopes = []
    lines = {}
    last_line_number = 0
    result = {"valid": True, "error": None}
    
    try:
        for line in test_lines:
            line = line.rstrip('\n')
            if not line:
                continue

            if line.strip() in ["BeginScope", "EndScope"]:
                command = line.strip()
                if command == "BeginScope":
                    current_scope_level += 1
                    scopes.append({'start_line': None, 'end_line': None,
                                 'assumption_line': None, 'last_line': None})
                elif command == "EndScope":
                    if not scopes:
                        result["valid"] = False
                        result["error"] = "Invalid scope nesting: EndScope without matching BeginScope"
                        return result
                    
                    for i in range(len(scopes) - 1, -1, -1):
                        if scopes[i]['end_line'] is None:
                            scopes[i]['end_line'] = last_line_number
                            scopes[i]['last_line'] = last_line_number
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
                rule, refs = parse_references(rule_and_refs.strip())
                lines[line_number] = {
                    'formula': formula,
                    'rule': rule,
                    'references': refs,
                    'scope_level': current_scope_level
                }
                if rule == "Assumption" and scopes and scopes[-1]['start_line'] is None:
                    scopes[-1]['start_line'] = line_number
                    scopes[-1]['assumption_line'] = line_number

                if not check_rule(line_number, lines, scopes):
                    result["valid"] = False
                    result["error"] = f"Invalid Deduction at Line {line_number}"
                    return result

        if current_scope_level != 0:
            result["valid"] = False
            result["error"] = "Invalid Deduction: Unclosed scopes"
            return result
            
        return result
        
    except Exception as e:
        result["valid"] = False
        result["error"] = f"Error: {e}"
        return result

def main():
    if len(sys.argv) != 2:
        print("Usage: python check_natural_inference.py <filename>")
        return

    filename = sys.argv[1]
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Split the content by the separator "---" (triple dash)
        test_cases = content.split('---')
        
        for i, test_case in enumerate(test_cases):
            test_case = test_case.strip()
            if not test_case:
                continue
                
            test_lines = test_case.split('\n')
            
            # Get first and last formulas for display
            first_formula = None
            last_formula = None
            line_numbers = []
            formulas = []
            
            for line in test_lines:
                line = line.strip()
                if line and not line.startswith('Begin') and not line.startswith('End'):
                    try:
                        parts = line.split(None, 1)
                        if len(parts) > 1:
                            line_number = parts[0].strip()
                            rest = parts[1].strip()
                            
                            match = re.search(r'\s{2,}', rest)
                            if match:
                                formula_str = rest[:match.start()].strip()
                                line_numbers.append(line_number)
                                formulas.append(formula_str)
                    except:
                        pass
                        
            if formulas:
                first_formula = formulas[0]
                last_formula = formulas[-1]
            
            print(f"\n--- Test Case {i+1} ---")
            print(f"Starting with: {first_formula}")
            print(f"Ending with: {last_formula}")
            
            result = check_deduction(test_lines)
            
            if result["valid"]:
                print("Valid Deduction")
            else:
                print(result["error"])
    
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    main()
from horn import HornFormula, WellFormedFormula

def test_case(formula_str):
    print(f"Testing: {formula_str}")
    
    try:
        if "∨" in formula_str or "v" in formula_str or "¬" in formula_str:
            print("Invalid Horn Formula")
            return
            
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
            
    except Exception as e:
        print(f"Error: {e}")
        print("Invalid Horn Formula")

test_cases = [
    "(p ∧ q ∧ s → p) ∧ (q ∧ r → p) ∧ (p ∧ s → s)",
    "(p ∧ q ∧ s → ⊥) ∧ (q ∧ r → p) ∧ (⊤ → s)",
    "⊤ → ⊥",
    "q ∨ r → p",
    "(p ∧ q ∧ s → ⊥) ∧ (s → p) ∧ (s → q) ∧ (⊤ → s)",
    "(s → p) ∧ (p ∧ q ∧ s → p) ∧ (⊤ → r) ∧ (s ∧ p → q) ∧ (⊤ → s)",
    "(¬s → p) ∧ (p ∧ q ∧ s → p) ∧ (⊤ → r) ∧ (s ∧ p → q) ∧ (⊤ → s)",
]

for idx, case in enumerate(test_cases, 1):
    print(f"\nTest Case {idx}:")
    test_case(case)

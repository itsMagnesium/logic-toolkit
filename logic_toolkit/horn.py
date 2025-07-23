from logic_toolkit.base import ParseTree, Node
from logic_toolkit.wff import WellFormedFormula
from typing import Optional, Union, Set, List, Tuple

class HornFormula(ParseTree):
    def __init__(self, formula: Optional[Union[WellFormedFormula, str]] = None) -> None:
        super().__init__()
        if isinstance(formula, str):
            if "∨" in formula or "v" in formula or "|" in formula or "¬" in formula:
                self._root = None
                self.is_valid_horn = False
                return
            
            formula = formula.replace('&', '∧').replace('^', '∧').replace('->', '→').replace('=>', '→')
            formula = formula.replace('T', '⊤').replace('F', '⊥').replace('true', '⊤').replace('false', '⊥')
            
            formula = WellFormedFormula(formula)
        elif not isinstance(formula, WellFormedFormula):
            raise TypeError("Expected a WellFormedFormula or a string representation of a formula.")
        
        self._root = formula.root.copy()
        self.is_valid_horn = self.__validate_horn_formula(self._root)
        
    def __validate_horn_formula(self, root: Node) -> bool:
        if root is None:
            return True
            
        if root.value in ['⊤', '⊥']:
            return root.left is None and root.right is None
            
        if root.value.islower() and len(root.value) == 1:
            return root.left is None and root.right is None
            
        if root.value == '∧':
            left_valid = self.__validate_horn_formula(root.left)
            right_valid = self.__validate_horn_formula(root.right)
            return left_valid and right_valid
        
        if root.value == '→':
            if not self.__is_single_literal_or_constant(root.right):
                return False
            
            return self.__validate_antecedent(root.left)
        
        if root.value == '∨':
            return False
        
        return False
        
    def __validate_antecedent(self, node: Node) -> bool:
        if node is None:
            return True
            
        if (node.value.islower() and len(node.value) == 1) or node.value in ['⊤', '⊥']:
            return node.left is None and node.right is None
            
        if node.value == '∧':
            left_valid = ((node.left.value.islower() and len(node.left.value) == 1) or 
                         node.left.value in ['⊤', '⊥']) and node.left.left is None and node.left.right is None
            
            right_valid = self.__validate_antecedent(node.right)
            
            return left_valid and right_valid
            
        return False
    
    def __is_single_literal_or_constant(self, node: Node) -> bool:
        if node is None:
            return True
            
        if node.value.islower() and len(node.value) == 1:
            return node.left is None and node.right is None
            
        if node.value in ['⊤', '⊥']:
            return node.left is None and node.right is None
            
        return False
        
    def __extract_horn_clauses(self, root: Node) -> List[Tuple[Set[str], str]]:
        clauses = []
        
        if root is None:
            return clauses
            
        if root.value == '→':
            antecedent_vars = set()
            self.__extract_antecedent_vars(root.left, antecedent_vars)
            consequent = root.right.value
            clauses.append((antecedent_vars, consequent))
            return clauses
        elif root.value in ['⊤', '⊥']:
            return [(set(['⊤']), root.value)]
        elif root.value.islower() and len(root.value) == 1:
            return [(set(), root.value)]
        elif root.value == '∧':
            left_clauses = self.__extract_horn_clauses(root.left)
            right_clauses = self.__extract_horn_clauses(root.right)
            return left_clauses + right_clauses
            
        return clauses
        
    def __extract_antecedent_vars(self, node: Node, vars_set: Set[str]) -> None:
        if node is None:
            return
            
        if node.value == '∧':
            self.__extract_antecedent_vars(node.left, vars_set)
            self.__extract_antecedent_vars(node.right, vars_set)
        elif node.value.islower() and len(node.value) == 1:
            vars_set.add(node.value)
        elif node.value == '⊤':
            vars_set.add('⊤')
            
    def check_satisfiability(self) -> Tuple[bool, Set[str]]:
        if not self.is_valid_horn:
            return False, set()
            
        if (self._root.value == '→' and 
            self._root.left and self._root.left.value == '⊤' and 
            self._root.right and self._root.right.value == '⊥'):
            return False, set()
            
        if self._root.value == '⊤':
            return True, set()
        if self._root.value == '⊥':
            return False, set()
            
        horn_clauses = self.__extract_horn_clauses(self._root)
        
        true_vars = set()
        true_vars.add('⊤')
                
        changed = True
        while changed:
            changed = False
            for antecedent, consequent in horn_clauses:
                if '⊤' in antecedent and len(antecedent) == 1:
                    if consequent not in true_vars and consequent != '⊥':
                        true_vars.add(consequent)
                        changed = True
                    elif consequent == '⊥':
                        return False, set()
                
                elif antecedent and antecedent.issubset(true_vars) and consequent not in true_vars and consequent != '⊥':
                    true_vars.add(consequent)
                    changed = True
                elif antecedent and antecedent.issubset(true_vars) and consequent == '⊥':
                    return False, set()
        
        if '⊤' in true_vars:
            true_vars.remove('⊤')
            
        return True, true_vars

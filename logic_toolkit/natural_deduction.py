from typing import List, Dict, Union, Tuple, Optional
from logic_toolkit.base import Node, ParseTree

class NaturalDeduction:
    def __init__(self) -> None:
        self.__rules = {
            '∧i': self.__and_introduction,
            '∧e1': self.__and_elimination_1,
            '∧e2': self.__and_elimination_2,
            '∨i1': self.__or_introduction_1,
            '∨i2': self.__or_introduction_2,
            '∨e': self.__or_elimination,
            '→i': self.__implication_introduction,
            '→e': self.__implication_elimination,
            '¬i': self.__negation_introduction,
            '¬e': self.__negation_elimination,
            '⊥e': self.__false_elimination,
            '¬¬e': self.__double_negation_elimination,
            'MT': self.__modus_tollens,
            '¬¬i': self.__double_negation_introduction,
            'PBC': self.__proof_by_contradiction,
            'LEM': self.__law_of_excluded_middle,
            'Copy': self.__copy
        }

    def __find_scope(self, scopes: List[Dict], start: int, end: int) -> Optional[Dict]:
        return next((s for s in scopes if s['start'] == start and s['end'] == end), None)

    def __is_reference_valid(self, reference: Union[int, Tuple[int, int]], current_line_number: int, lines: List[Dict], scopes: Optional[List[Dict]] = None) -> bool:
        if isinstance(reference, int):
            if reference not in lines or reference >= current_line_number:
                return False
            
            if scopes is None:
                return True
            
            current_scope_level = lines[current_line_number]['scope_level']
            referenced_scope_level = lines[reference]['scope_level']
            
            if referenced_scope_level < current_scope_level:
                return True
            
            if referenced_scope_level == current_scope_level:
                if current_scope_level == 0:
                    return True
                
                for scope in scopes:
                    if scope['start'] is not None:
                        if scope['end'] is None:
                            if (scope['start'] <= reference and scope['start'] <= current_line_number):
                                return True
                        else:
                            if (scope['start'] <= reference <= scope['end'] and scope['start'] <= current_line_number <= scope['end']):
                                return True
                return False
            
            return False
        
        elif isinstance(reference, tuple):
            start, end = reference
            if scopes is None:
                return False
            
            scope = self.__find_scope(scopes, start, end)
            return scope is not None and end < current_line_number
        
        return False

    def __validate_all_references(self, references: List[Union[int, Tuple[int, int]]], current_line_number: int, lines: List[Dict], scopes: Optional[List[Dict]] = None) -> bool:
        return all(self.__is_reference_valid(ref, current_line_number, lines, scopes) for ref in references)

    def apply_rule(self, rule_name: str, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if rule_name not in self.__rules:
            raise ValueError(f"Unknown rule: {rule_name}")

        return self.__rules[rule_name](lines, references, scopes)

    def check_rule(self, line_number: int, lines: List[Dict], scopes: Optional[List[Dict]] = None) -> bool:
        line = lines[line_number]
        rule_name: str = line['rule']
        references: List[Union[int, Tuple[int, int]]] = line['references']
        formula: ParseTree = line['formula']

        if rule_name in ["Premise", "Assumption"]:
            return True

        if rule_name not in self.__rules:
            raise ValueError(f"Unknown rule: {rule_name}")

        if not self.__validate_all_references(references, line_number, lines, scopes):
            return False
        if rule_name in ['⊥e', '∨i1', '∨i2', 'LEM']:
            references.append(line_number)
        expected_tree = self.apply_rule(rule_name, lines, references, scopes)
        return expected_tree == formula

    def __and_introduction(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 2:
            raise ValueError("Expected two references for ∧i rule.")

        formulas: List[ParseTree] = [lines[ref]['formula'] for ref in references]        

        root = Node(
            value='∧',
            left=formulas[0].root.copy(),
            right=formulas[1].root.copy()
        )
        return ParseTree(root)

    def __and_elimination_1(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 1:
            raise ValueError("Expected one reference for ∧e1 rule.")

        formula: ParseTree = lines[references[0]]['formula']
        if formula.root.value != '∧':
            raise ValueError("Expected a conjunction (A ∧ B) for ∧e1 rule.")

        return ParseTree(root=formula.root.left.copy())

    def __and_elimination_2(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 1:
            raise ValueError("Expected one reference for ∧e2 rule.")

        formula: ParseTree = lines[references[0]]['formula']
        if formula.root.value != '∧':
            raise ValueError("Expected a conjunction (A ∧ B) for ∧e2 rule.")

        return ParseTree(root=formula.root.right.copy())

    def __or_introduction_1(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 2:
            raise ValueError("Expected two references for ∨i1 rule.")

        formulas: List[ParseTree] = [lines[ref]['formula'] for ref in references]
        if formulas[0].root == formulas[1].root.left:
            return formulas[1]
        
        raise ValueError("Incorrect Use of ∨i1 rule.")
    

    def __or_introduction_2(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 2:
            raise ValueError("Expected two references for ∨i2 rule.")

        formulas: List[ParseTree] = [lines[ref]['formula'] for ref in references]
        if formulas[0].root == formulas[1].root.right:
            return formulas[1]
        
        raise ValueError("Incorrect Use of ∨i2 rule.")

    def __or_elimination(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 3:
            raise ValueError("Expected three references for ∨e rule.")
        if not isinstance(references[0], int) or not all(isinstance(r, tuple) for r in references[1:]):
            raise ValueError("Expected one reference and two scopes for ∨e rule.")

        line, (s1, e1), (s2, e2) = references

        or_formula: ParseTree = lines[line]['formula']
        if or_formula.root.value != '∨':
            raise ValueError("Expected a disjunction (A ∨ B) for ∨e rule.")
        if not self.__find_scope(scopes, s1, e1) or \
            not self.__find_scope(scopes, s2, e2) or \
            lines[s1]['scope_level'] != lines[s2]['scope_level']:
            raise ValueError("Invalid scopes for ∨e rule.")
        if (or_formula.root.left != lines[s1]['formula'].root and or_formula.root.right != lines[s1]['formula'].root) or (or_formula.root.left != lines[s2]['formula'].root and or_formula.root.right != lines[s2]['formula'].root):
            raise ValueError("The formulas in the scopes must match the operands of the disjunction.")

        if lines[s1]['formula'] != ParseTree(or_formula.root.left.copy()):
            raise ValueError("Left scope does not match the left operand of the disjunction.")
        if lines[s2]['formula'] != ParseTree(or_formula.root.right.copy()):
            raise ValueError("Right scope does not match the right operand of the disjunction.")
        
        if lines[e1]['formula'] != lines[e2]['formula']:
            raise ValueError("The formulas in the scopes must be equal for ∨e rule.")
        
        return lines[e1]['formula']

    def __implication_introduction(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 1 or not isinstance(references[0], tuple):
            raise ValueError("Expected one scope for →i rule.")

        start, end = references[0]
        if not self.__find_scope(scopes, start, end):
            raise ValueError("Invalid scope for →i rule.")

        if lines[start]['rule'] != 'Assumption':
            raise ValueError("The starting line must be an assumption for →i rule.")

        antecedent: ParseTree = lines[start]['formula']
        consequent: ParseTree = lines[end]['formula']

        root = Node(
            value='→',
            left=antecedent.root.copy(),
            right=consequent.root.copy()
        )
        return ParseTree(root)

    def __implication_elimination(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 2:
            raise ValueError("Expected two references for →e rule.")

        formulas: List[ParseTree] = [lines[ref]['formula'] for ref in references]

        if formulas[0].root.value != '→' and formulas[1].root.value != '→':
            raise ValueError("Expected an implication (A → B) for →e rule.")

        if formulas[0].root.value == '→' and formulas[0].root.left == formulas[1].root:
            return ParseTree(root=formulas[0].root.right.copy())

        elif formulas[1].root.value == '→' and formulas[1].root.left == formulas[0].root:
            return ParseTree(root=formulas[1].root.right.copy())

        raise ValueError("Cannot apply →e rule to the given references.")

    def __negation_introduction(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 1 or not isinstance(references[0], tuple):
            raise ValueError("Expected one scope for ¬i rule.")
        
        start, end = references[0]
        if not self.__find_scope(scopes, start, end):
            raise ValueError("Invalid scope for ¬i rule.")

        if lines[start]['rule'] != 'Assumption':
            raise ValueError("The starting line must be an assumption for ¬i rule.")
        if lines[end]['formula'].root.value != '⊥':
            raise ValueError("The ending line must be false (⊥) for ¬i rule.")
        
        negated_formula = Node(
            value='¬',
            right=lines[start]['formula'].root.copy()
        )
        return ParseTree(negated_formula)

    def __negation_elimination(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 2:
            raise ValueError("Expected two references for ¬e rule.")

        formulas: List[ParseTree] = [lines[ref]['formula'] for ref in references]

        if (formulas[0].root.value == '¬' and formulas[0].root.right == formulas[1].root) or \
           (formulas[1].root.value == '¬' and formulas[1].root.right == formulas[0].root):
            return ParseTree(Node(value='⊥'))

        raise ValueError("Cannot apply ¬e rule to the given references.")

    def __false_elimination(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 2:
            raise ValueError("Expected two references for ⊥e rule.")

        formulas: List[ParseTree] = [lines[ref]['formula'] for ref in references]

        if formulas[0].root.value == '⊥':
            return formulas[1]

        raise ValueError("Cannot apply ⊥e rule to the given references.")

    def __double_negation_elimination(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 1:
            raise ValueError("Expected one reference for ¬¬e rule.")

        formula: ParseTree = lines[references[0]]['formula']

        if formula.root.value == '⊥':
            return formula

        raise ValueError("Cannot apply ⊥e rule to the given reference.")

    def __double_negation_elimination(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 1:
            raise ValueError("Expected one reference for ¬¬e rule.")

        formula: ParseTree = lines[references[0]]['formula']

        if (formula.root.value == '¬' and
            formula.root.right.value == '¬'):
            return ParseTree(formula.root.right.right.copy())

        raise ValueError("Cannot apply ¬¬e rule to the given references.")

    def __modus_tollens(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 2:
            raise ValueError("Expected two references for MT rule.")

        formulas: List[ParseTree] = [lines[ref]['formula'] for ref in references]
        implication, negation = (formulas[0], formulas[1]) if formulas[0].root.value == '→' else (formulas[1], formulas[0])

        if implication.root.value != '→' or negation.root.value != '¬':
            raise ValueError("Expected an implication (A → B) and a negation (¬B) for MT rule.")

        if implication.root.right == negation.root.right:
            root = Node(
                value='¬',
                right=implication.root.left.copy()
            )
            return ParseTree(root)

        raise ValueError("Cannot apply MT rule to the given references.")

    def __double_negation_introduction(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 1:
            raise ValueError("Expected one reference for ¬¬i rule.")

        formula: ParseTree = lines[references[0]]['formula']

        root = Node(
            value='¬',
            right=Node(
                value='¬',
                right=formula.root.copy()
            )
        )
        return ParseTree(root)

    def __proof_by_contradiction(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 1 or not isinstance(references[0], tuple):
            raise ValueError("Expected one scope for PBC rule.")

        start, end = references[0]
        if not self.__find_scope(scopes, start, end):
            raise ValueError("Invalid scope for PBC rule.")

        if lines[start]['rule'] != 'Assumption':
            raise ValueError("The starting line must be an assumption for PBC rule.")

        assumption: ParseTree = lines[start]['formula']
        if lines[end]['formula'].root.value != '⊥':
            raise ValueError("The ending line must be false (⊥) for PBC rule.")
        
        if assumption.root.value == '¬':
            return ParseTree(assumption.root.right.copy())
        else:
            root = Node(value='¬', right=assumption.root)
            return ParseTree(root)

    def __law_of_excluded_middle(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 1:
            raise ValueError("Expected one reference for LEM rule.")

        formula: ParseTree = lines[references[0]]['formula']
        if formula.root.value != '∨':
            raise ValueError("Expected a disjunction (A ∨ ¬A) for LEM rule.")
        if formula.root.left.value == '¬' and formula.root.left.right == formula.root.right or \
            formula.root.right.value == '¬' and formula.root.right.right == formula.root.left:
            return formula

        raise ValueError("Incorrect use of LEM rule. The formula must be of the form A ∨ ¬A.")

    def __copy(self, lines: List[Dict], references: List[Union[int, Tuple[int, int]]], scopes: Optional[List[Dict]] = None) -> ParseTree:
        if len(references) != 1:
            raise ValueError("Expected one reference for copy rule.")

        formula: ParseTree = lines[references[0]]['formula']
        return ParseTree(formula.root.copy())

    @classmethod
    def parse_references(cls, ref_str: str) -> Tuple[str, List[Union[int, Tuple[int, int]]]]:
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
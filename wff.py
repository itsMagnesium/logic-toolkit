from base import ParseTree, Node
from typing import Union

class WellFormedFormula(ParseTree):
    def __init__(self, formula: str) -> None:
        super().__init__()
        self.__from_string(formula)

    def __from_string(self, formula: str) -> "WellFormedFormula":
        if self.is_built:
            raise ValueError("ParseTree is already built. Create a new instance to parse a different formula.")
        
        formula = formula.replace(' ', '')
        if not formula:
            raise ValueError("Empty formula")

        self._root = self.__parse_expression(formula)
        return self
    
    def __parse_expression(self, formula: str) -> Node:
        formula = formula
        if not formula:
            raise ValueError("Empty expression")

        while formula.startswith('(') and formula.endswith(')') and self.__matching_parenthesis(formula, 0) == len(formula) - 1:
            formula = formula[1:-1]
        
        main_op_pos = self.__find_main_operator(formula)
        
        if main_op_pos == -1:
            if formula.startswith('¬'):
                operand = formula[1:]
                if not operand:
                    raise ValueError("Missing operand for negation")
                neg_node = Node('¬')
                neg_node.right = self.__parse_expression(operand)
                return neg_node
            # Special constants first
            elif formula in ['⊤', '⊥', 'T', 'F', 'true', 'false']:
                # Normalize to standard symbols
                if formula in ['T', 'true']:
                    return Node('⊤')
                elif formula in ['F', 'false']:
                    return Node('⊥')
                else:
                    return Node(formula)
            # Then check for propositional variables
            elif len(formula) == 1 and formula.isalpha():
                return Node(formula)
            else:
                raise ValueError(f"Invalid expression: {formula}")
        
        left_expr = formula[:main_op_pos]
        operator = formula[main_op_pos]
        right_expr = formula[main_op_pos + 1:]
        
        if not left_expr or not right_expr:
            raise ValueError(f"Missing operand for operator {operator}")
        
        op_node = Node(operator)
        op_node.left = self.__parse_expression(left_expr)
        op_node.right = self.__parse_expression(right_expr)
        
        return op_node
    
    def __find_main_operator(self, formula: str) -> int:
        # Operator precedence (lower number = lower precedence)
        precedence = {'→': 1, '∨': 2, '∧': 3}
        
        main_op_pos = -1
        main_op_precedence = float('inf')
        paren_level = 0
        
        for i, char in enumerate(formula):
            if char == '(':
                paren_level += 1
            elif char == ')':
                paren_level -= 1
            elif paren_level == 0 and char in precedence:
                char_precedence = precedence[char]
                if char_precedence < main_op_precedence:
                    main_op_pos = i
                    main_op_precedence = char_precedence
                elif char_precedence == main_op_precedence:
                    if char == '→':
                        pass
                    else:
                        main_op_pos = i
        
        return main_op_pos

    def __matching_parenthesis(self, formula: str, start: int) -> int:
        if formula[start] != '(':
            return -1
        
        paren_count = 1
        for i in range(start + 1, len(formula)):
            if formula[i] == '(':
                paren_count += 1
            elif formula[i] == ')':
                paren_count -= 1
                if paren_count == 0:
                    return i
        
        return -1
    
    @classmethod
    def is_valid(cls, formula: str) -> Union["WellFormedFormula", None]:
        try:
            new_instance = cls(formula)
            print('Valid Formula')
            print(new_instance.preorder())
            return new_instance
        except ValueError:
            print('Invalid Formula')
            return None
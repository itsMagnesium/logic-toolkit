from typing import Union

class Node:
    def __init__(self, value: str,  left: "Node" = None, right: "Node" = None) -> None:
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Node(value='{self.value}', left={f"'{self.left.value}'" if self.left else None}, right={f"'{self.right.value}'" if self.right else None})"

    def __str__(self):
        return self.value

    @property
    def left(self) -> "Node":
        return self.__left

    @property
    def right(self) -> "Node":
        return self.__right

    @right.setter
    def right(self, node: Union["Node", None]) -> None:
        if isinstance(node, Node) or node is None:
            self.__right = node
        else:
            raise TypeError("Right child must be a Node instance or None.")

    @left.setter  
    def left(self, node: Union["Node", None]) -> None:
        if isinstance(node, Node) or node is None:
            self.__left = node
        else:
            raise TypeError("Left child must be a Node instance or None.")

class ParseTree:
    def __init__(self, formula: str = None) -> None:
        self.__root: Node = None
        if formula is not None:
            self.from_string(formula)
    
    def __repr__(self):
        return f'ParseTree(formula="{self.__str__()}")'

    def __str__(self):
        inorder_nodes = self.__inorder()
        return "".join(node.value for node in inorder_nodes)

    def __inorder(self) -> list[Node]:
        if not self.is_built:
            return []
        result = []
        def _inorder(node: Node):
            if node is not None:
                _inorder(node.left)
                result.append(node)
                _inorder(node.right)
        _inorder(self.__root)
        return result
    
    def preorder(self) -> str:
        if not self.is_built:
            return ""
        
        result = []
        
        def _preorder(node: Node, depth: int = 0):
            if node is not None:
                indent = "  " * depth
                result.append(f"{indent}{node.value}")
                _preorder(node.left, depth + 1)
                _preorder(node.right, depth + 1)
        
        _preorder(self.__root)
        return "\n".join(result)

    @property
    def is_built(self) -> bool:
        return self.__root is not None

    @property
    def root(self) -> Node:
        return self.__root
    
    def from_string(self, formula: str) -> "ParseTree":
        if self.is_built:
            raise ValueError("ParseTree is already built. Create a new instance to parse a different formula.")
        
        formula = formula.replace(' ', '')
        if not formula:
            raise ValueError("Empty formula")
        
        self.__root = self.__parse_expression(formula)
        return self
    
    def __parse_expression(self, formula: str) -> Node:
        formula = formula
        if not formula:
            raise ValueError("Empty expression")

        while formula.startswith('(') and formula.endswith(')') and self.__matching_parenthesis(formula, 0) == len(formula) - 1:
            formula = formula[1:-1]
        
        if formula.startswith('¬'):
            operand = formula[1:]
            if not operand:
                raise ValueError("Missing operand for negation")
            neg_node = Node('¬')
            neg_node.right = self.__parse_expression(operand)
            return neg_node

        main_op_pos = self.__find_main_operator(formula)
        
        if main_op_pos == -1:
            if len(formula) == 1 and formula.isalpha():
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
                if char_precedence <= main_op_precedence:
                    main_op_pos = i
                    main_op_precedence = char_precedence
        
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
    def is_valid(cls, formula: str) -> Union["ParseTree", None]:
        try:
            new_instance = cls()
            new_instance.from_string(formula)
            print('Valid Formula')
            print(new_instance.preorder())
            return new_instance
        except ValueError:
            print('Invalid Formula')
            return None
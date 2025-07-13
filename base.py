from collections import deque
from typing import Union

class Node:
    def __init__(self, value: str,  left: "Node" = None, right: "Node" = None) -> None:
        self.value = value
        self.__left = left
        self.__right = right

    def __repr__(self):
        return f"Node(value={self.value}, left={repr(self.__left)}, right={repr(self.__right)})"

    def __str__(self):
        return self.value

    @property
    def left(self) -> "Node":
        return self.__left

    @property
    def right(self) -> "Node":
        return self.__right

    @right.setter
    def right(self, node: "Node") -> None:
        if node is None or not isinstance(node, Node):
            raise ValueError("Right child must be a Node instance.")
        self.__right = node

    @left.setter
    def left(self, node: "Node") -> None:
        if node is None or not isinstance(node, Node):
            raise ValueError("Left child must be a Node instance.")
        self.__left = node

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
        # TODO: This method should be fixed, there are several cases in which the method malfunctions.
        if self.is_built:
            raise ValueError("ParseTree is already built. Create a new instance to parse a different formula.")
        
        formula = formula.replace(' ', '')
        current = Node(value='')
        stack = deque([current])
        current.left = Node(value='')
        current = current.left
        for token in list(formula):
            if token == '(':
                stack.append(current)
                current.left = Node(value='')
                current = current.left
            elif token in ['¬', '→', '∧', '∨']:
                stack.append(current)
                current.value = token
                current.right = Node(value='')
                current = current.right
            elif token == ')':
                current = stack.pop()
            elif token.isalpha():
                current.value = token
                current = stack.pop() if stack else None
            else:
                raise ValueError(f"Invalid token in formula: {token}")
        if stack:
            raise ValueError("Unmatched parentheses in formula.")
        self.__root = current
        return self
    
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
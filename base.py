from typing import Union
from copy import deepcopy

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
    
    def copy(self) -> "Node":
        return deepcopy(self)

class ParseTree:
    def __init__(self) -> None:
        self._root: Node = None
    
    def __repr__(self):
        if not self.is_built:
            return f'{self.__class__.__name__}()'
        else:
            return f'{self.__class__.__name__}(formula="{self.__str__()}")'

    def __str__(self):
        if not self.is_built:
            return ""
        return self._node_to_string(self._root)

    def _node_to_string(self, node: Node) -> str:
        if node is None:
            return ""
        
        if node.value == '¬':
            operand = self._node_to_string(node.right)
            if node.right and node.right.value in ['→', '∧', '∨']:
                operand = f"({operand})"
            return f"¬{operand}"
        elif node.value in ['→', '∧', '∨']:
            left = self._node_to_string(node.left)
            right = self._node_to_string(node.right)
            
            precedence = {'→': 1, '∨': 2, '∧': 3}
            current_prec = precedence[node.value]
            
            if (node.left and node.left.value in precedence):
                left_prec = precedence[node.left.value]
                if (left_prec < current_prec or 
                    (left_prec == current_prec and node.value == '→')):
                    left = f"({left})"
           
            if (node.right and node.right.value in precedence):
                right_prec = precedence[node.right.value]
                if right_prec < current_prec:
                    right = f"({right})"
            
            return f"{left} {node.value} {right}"
        else:
            return node.value
    
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
        
        _preorder(self._root)
        return "\n".join(result)

    @property
    def is_built(self) -> bool:
        return self._root is not None

    @property
    def root(self) -> Node:
        return self._root
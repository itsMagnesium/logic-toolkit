from typing import Optional
from copy import deepcopy

class Node:
    def __init__(self, value: str,  left: Optional["Node"] = None, right: Optional["Node"] = None) -> None:
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"Node(value='{self.value}', left={f"'{self.left.value}'" if self.left else None}, right={f"'{self.right.value}'" if self.right else None})"

    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: "Node") -> bool:
        if not isinstance(other, Node):
            return False
        return self.value == other.value and self.left == other.left and self.right == other.right

    @property
    def left(self) -> Optional["Node"]:
        return self.__left

    @property
    def right(self) -> Optional["Node"]:
        return self.__right

    @right.setter
    def right(self, node: Optional["Node"]) -> None:
        if isinstance(node, Node) or node is None:
            self.__right = node
        else:
            raise TypeError("Right child must be a Node instance or None.")

    @left.setter  
    def left(self, node: Optional["Node"]) -> None:
        if isinstance(node, Node) or node is None:
            self.__left = node
        else:
            raise TypeError("Left child must be a Node instance or None.")
    
    def copy(self) -> "Node":
        return deepcopy(self)

class ParseTree:
    def __init__(self, root: Optional[Node] = None) -> None:
        self._root = root

    def __repr__(self) -> str:
        if not self.is_built:
            return f'{self.__class__.__name__}()'
        else:
            return f'{self.__class__.__name__}(formula="{self.__str__()}")'

    def __str__(self) -> str:
        if not self.is_built:
            return ""
        return self._node_to_string(self._root)

    def __eq__(self, other: "ParseTree") -> bool:
        if not isinstance(other, ParseTree):
            return False
        return self._root == other._root

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
    def root(self) -> Optional[Node]:
        return self._root
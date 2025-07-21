from base import ParseTree, Node
from wff import WellFormedFormula
from typing import Union

class CNF(ParseTree):
    def __init__(self, formula: Union[WellFormedFormula, str] = None) -> None:
        super().__init__()
        if isinstance(formula, str):
            formula = WellFormedFormula(formula)
        elif not isinstance(formula, WellFormedFormula):
            raise TypeError("Expected a WellFormedFormula or a string representation of a formula.")
        
        self._root = self.__convert_to_cnf(formula.root.copy())

    def __convert_to_cnf(self, root: Node) -> Node:
        if root is None:
            raise ValueError("Cannot convert an empty formula to CNF.")
        
        root = self.__eliminate_implications(root)
        root = self.__de_morgan(root)
        root = self.__distribute_or_over_and(root)

        return root
    
    def __eliminate_implications(self, root: Node) -> Node:
        if root is None:
            return None

        root.left = self.__eliminate_implications(root.left)
        root.right = self.__eliminate_implications(root.right)

        if root.value == '→':
            left_node = Node(value='¬', right=root.left)
            new_root = Node(value='∨', left=left_node, right=root.right)
            return new_root

        return root

    def __de_morgan(self, root: Node) -> Node:
        if root is None:
            return None
        
        if root.value == '¬':
            match root.right.value:
                case '¬':
                    root = root.right.right
                case '∧':
                    left_node = Node(value='¬', right=root.right.left)
                    right_node = Node(value='¬', right=root.right.right)
                    root = Node(value='∨', left=left_node, right=right_node)
                case '∨':
                    left_node = Node(value='¬', right=root.right.left)
                    right_node = Node(value='¬', right=root.right.right)
                    root = Node(value='∧', left=left_node, right=right_node)
                

        root.left = self.__de_morgan(root.left)
        root.right = self.__de_morgan(root.right)
    
        return root
    
    def __distribute_or_over_and(self, root: Node) -> Node:
        if root is None:
            return None
        
        if root.value == '∨':
            if root.left and root.left.value == '∧': # (A ∧ B) ∨ C
                left_node = Node(
                    value='∨',
                    left=root.left.left.copy(),
                    right=root.right.copy()
                )

                right_node = Node(
                    value='∨',
                    left=root.left.right.copy(),
                    right=root.right.copy()
                )

                root = Node(
                    value='∧',
                    left=left_node,
                    right=right_node
                )

            elif root.right and root.right.value == '∧': # A ∨ (B ∧ C) 
                left_node = Node(
                    value='∨',
                    left=root.left.copy(),
                    right=root.right.left.copy()
                )

                right_node = Node(
                    value='∨',
                    left=root.left.copy(),
                    right=root.right.right.copy()
                )

                root = Node(
                    value='∧',
                    left=left_node,
                    right=right_node
                )
        
        root.left = self.__distribute_or_over_and(root.left)
        root.right = self.__distribute_or_over_and(root.right)

        return root
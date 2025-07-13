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
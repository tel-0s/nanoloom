from nanoloom.tapestry import Tapestry, Node
from nanoloom.backends.core import load_backend
from nanoloom.utils import to_dict
from uuid import uuid4

from typing import Dict, Any, List

class Shuttle:
    def __init__(self, tapestry: 'Tapestry', node: str, backend: str):
        self.tapestry = tapestry
        self.node = node
        self.backend = load_backend(backend)

    def get_state(self) -> Node:
        """Recurse up the tree to get the state of the data at the current node"""
        node = self.tapestry[self.node]
        state = node.data
        while node.parent:
            node = self.tapestry[node.parent]
            state = node.data + state
        return state
    
    def get_node(self) -> Node:
        """Return the current node"""
        return self.tapestry[self.node]
    
    def list_children(self) -> None:
        """Print the children of the current node"""
        print("children:")
        for i, child in enumerate(self.tapestry[self.node].children):
            print(f'{i+1}: {self.tapestry[child].data}\n')
    
    def forward(self, index=1) -> None:
        """Move the shuttle down <index> levels or until first node with multiple children (at which point query user)"""
        node = self.tapestry[self.node]
        if not node.children or index == 0:
            return
        elif len(node.children) > 1:
            self.list_children()
            index = input('choice> ')
            if index == '':
                return
            index = int(index)-1
            while index < 0 or index >= len(node.children):
                print('invalid choice')
                index = int(input('choice> '))
            self.node = node.children[index]
        else:
            self.node = node.children[0]

    def backward(self, index=1) -> None:
        """Move the shuttle up <index> levels or until the root node"""
        node = self.tapestry[self.node]
        while index > 0 and node.parent:
            node = self.tapestry[node.parent]
            index -= 1
        self.node = node.id

    def right(self) -> None:
        """Move the shuttle to the right sibling node"""
        node = self.tapestry[self.node]
        if node.parent:
            siblings = self.tapestry[node.parent].children
            idx = siblings.index(self.node)
            self.node = siblings[(idx + 1) % len(siblings)]

    def left(self) -> None:
        """Move the shuttle to the left sibling node"""
        node = self.tapestry[self.node]
        if node.parent:
            siblings = self.tapestry[node.parent].children
            idx = siblings.index(self.node)
            self.node = siblings[(idx - 1) % len(siblings)]

    def insert(self, data: str, metadata: Dict[str,Any]={}, goto=True) -> None:
        """Insert a new node with the given data at the current node"""
        node = self.tapestry[self.node]
        new_node = Node(str(uuid4()), data, metadata, node.id, [])
        node.children.append(new_node.id)
        self.tapestry[new_node.id] = new_node
        if goto:
            self.node = new_node.id

    def edit(self, data: str, goto=True) -> None:
        """Insert a new node with the given data as a sibling to the current node"""
        node = self.tapestry[self.node]
        new_node = Node(str(uuid4()), data, node.metadata, node.parent, [])
        self.tapestry.nodes[new_node.id] = new_node
        siblings = self.tapestry[node.parent].children
        idx = siblings.index(self.node)
        siblings.insert(idx + 1, new_node.id)
        if goto:
            self.node = new_node.id

    def generate(self, **kwargs) -> None:
        """Generate a new node with the given parameters, using the node's current state as the prompt"""
        prompt = self.get_state()
        completion = self.backend.complete(prompt, **kwargs)
        completion_dict = to_dict(completion)
        for choice in completion_dict.pop('choices'):
            data = choice.pop('text')
            metadata = completion_dict
            metadata.update(choice) # eventually we'll put this in a Warp instead (Arachne)
            self.insert(data, metadata, goto=False)
        self.forward()
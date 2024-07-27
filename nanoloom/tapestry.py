from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Node:
    """A tapestry node representing a concatenation of data"""
    id: str
    data: str
    metadata: Optional[Dict[str, Any]]
    parent: Optional[str]
    children: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.metadata = self.metadata or {}

class Tapestry:

    def __init__(self, nodes: Dict[str, Node], root: str, metadata: Optional[Dict[str, Any]] = None):
        self.nodes = nodes
        self.root = root
        self.metadata = metadata or {}

    def __getitem__(self, key: str) -> Node:
        return self.nodes[key]
    
    def __setitem__(self, key: str, value: Node) -> None:
        self.nodes[key] = value
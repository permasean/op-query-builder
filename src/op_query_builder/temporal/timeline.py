from typing import Union
from op_query_builder.elements.node import Node
from op_query_builder.elements.way import Way
from op_query_builder.elements.relation import Relation

class Timeline:
    def __init__(self, element: Union[Node, Way, Relation]) -> None:
        self.element = element
        self._validate()

    def _validate(self) -> None:
        if not isinstance(self.element, (Node, Way, Relation)):
            raise TypeError("Element must be a Node, Way, or Relation")
        if self.element.id is None and not self.element.ids:
            raise ValueError("Element must have an id or ids set for timeline")

    def __str__(self) -> str:
        element_type = "node" if isinstance(self.element, Node) else "way" if isinstance(self.element, Way) else "relation"
        element_id = self.element.id if self.element.id is not None else ",".join(map(str, self.element.ids))
        return f"timeline({element_type}({element_id}));"
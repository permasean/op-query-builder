from typing import Union
from op_query_builder.elements.node import Node
from op_query_builder.elements.way import Way
from op_query_builder.elements.relation import Relation

class Timeline:
    def __init__(self, element: Union[Node, Way, Relation]) -> None:
        """Initialize a Timeline statement for querying the history of an element in Overpass QL.

        Args:
            element (Union[Node, Way, Relation]): The element (Node, Way, or Relation) to query the timeline for.

        Raises:
            TypeError: If element is not a Node, Way, or Relation.
        """
        self.element = element
        self._validate()

    def _validate(self) -> None:
        """Validate the Timeline statement parameters.

        Raises:
            TypeError: If element is not a Node, Way, or Relation.
        """
        if not isinstance(self.element, (Node, Way, Relation)):
            raise TypeError(f"Element must be a Node, Way, or Relation, got {type(self.element).__name__}")

    def __str__(self) -> str:
        """Generate the Overpass QL query string for this Timeline statement.

        Returns:
            str: The Overpass QL query string.
        """
        element_str = str(self.element)
        if element_str.endswith(';'):
            element_str = element_str[:-1]
        return f"timeline({element_str});"
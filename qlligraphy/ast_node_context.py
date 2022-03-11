import ast
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, validator, Field  # pylint: disable=no-name-in-module

from .constants import GQL_TO_PY_SIMPLE_TYPE_MAP


class TopologicalSortStatus(str, Enum):
    NOT_RESOLVED = "not_resolved"
    VISITED = "visited"
    RESOLVED = "resolved"


class Imports(str, Enum):
    ENUM = "ENUM"
    PYDANTIC = "PYDANTIC"


class AstNodeContext(BaseModel):
    type: str
    node: ast.AST
    imports: Optional[Imports] = None
    dependencies: List["AstNodeContext"] = Field(default_factory=list)
    status: TopologicalSortStatus = TopologicalSortStatus.NOT_RESOLVED
    field_types: List[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

    @validator("dependencies")
    def dependency_is_not_simple_type(cls, value):
        return [
            dependency
            for dependency in value
            if dependency.type not in GQL_TO_PY_SIMPLE_TYPE_MAP.values()
        ]

    def build_dependencies(self, definition_map) -> None:
        self.dependencies = [definition_map[field] for field in self.field_types]


def topological_sort(nodes: List["AstNodeContext"]):
    sorted_list = []
    stack = nodes[:]

    while stack:
        considered_node = stack.pop()
        if considered_node.status == TopologicalSortStatus.VISITED:
            continue

        if (
            considered_node.status == TopologicalSortStatus.RESOLVED
            or not considered_node.dependencies
        ):
            sorted_list.append(considered_node)
            considered_node.status = TopologicalSortStatus.VISITED
        else:
            considered_node.status = TopologicalSortStatus.RESOLVED
            stack.append(considered_node)
            for dependency in considered_node.dependencies:
                stack.append(dependency)

    return sorted_list


def has_imports(definitions: List[AstNodeContext], import_: Imports) -> bool:
    return any(definition.imports == import_ for definition in definitions)

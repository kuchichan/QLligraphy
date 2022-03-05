import ast
from enum import Enum
from typing import Callable, Dict, Optional, List, Final

import graphql
from pydantic import BaseModel, validator  # pylint: disable=no-name-in-module

from .visitor import Visitor

GQL_TO_PY_SIMPLE_TYPE_MAP: Final[Dict[str, str]] = {
    "String": "str",
    "ID": "str",
    "Integer": "int",
    "Boolean": "bool",
    "Float": "float",
}


class TopologicalSortStatus(str, Enum):
    NOT_RESOLVED = "not_resolved"
    VISITED = "visited"
    RESOLVED = "resolved"


class AstNodeContext(BaseModel):
    node: ast.AST
    type: str
    dependencies: List["AstNodeContext"]
    status: TopologicalSortStatus = TopologicalSortStatus.NOT_RESOLVED

    class Config:
        arbitrary_types_allowed = True

    @validator("dependencies")
    def dependency_is_not_simple_type(cls, value):
        return [
            dependency
            for dependency in value
            if dependency.type not in GQL_TO_PY_SIMPLE_TYPE_MAP.values()
        ]


class GraphQLSchemaVisitor(Visitor[graphql.Node, AstNodeContext]):
    type_to_func_map: Dict[
        type[graphql.Node],
        Callable[["Visitor", graphql.Node, Optional[graphql.Node]], AstNodeContext],
    ] = {}
    blank_value = AstNodeContext(node=ast.Name(""), type="String", dependencies=[])

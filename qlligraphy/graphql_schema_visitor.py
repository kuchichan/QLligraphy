import ast
from typing import Callable, Dict, Optional, List, Final

import graphql
from pydantic import BaseModel, validator

from .visitor import Visitor

GQL_TO_PY_SIMPLE_TYPE_MAP: Final[Dict[str, str]] = {
    "String": "str",
    "ID": "str",
    "Integer": "int",
    "Boolean": "bool",
    "Float": "float",
}


class Context(BaseModel):
    node: ast.AST
    type: str
    dependencies: List[str]

    @validator("deps")
    def dependency_is_not_simple_type(cls, value):
        return [
            dependency
            for dependency in value
            if dependency not in GQL_TO_PY_SIMPLE_TYPE_MAP
        ]


class GraphQLSchemaVisitor(Visitor[graphql.Node, ast.AST]):
    type_to_func_map: Dict[
        type[graphql.Node],
        Callable[["Visitor", graphql.Node, Optional[graphql.Node]], ast.AST],
    ] = {}
    blank_value = ast.Name("")

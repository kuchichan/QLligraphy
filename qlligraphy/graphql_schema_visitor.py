import ast
from enum import Enum
from typing import Callable, Dict, Optional, List, Final

import graphql
from pydantic import BaseModel, validator  # pylint: disable=no-name-in-module

from .visitor import Visitor
from .ast_node_context import AstNodeContext

GQL_TO_PY_SIMPLE_TYPE_MAP: Final[Dict[str, str]] = {
    "String": "str",
    "ID": "str",
    "Integer": "int",
    "Boolean": "bool",
    "Float": "float",
}


class GraphQLSchemaVisitor(Visitor[graphql.Node, AstNodeContext]):
    type_to_func_map: Dict[
        type[graphql.Node],
        Callable[["Visitor", graphql.Node, Optional[graphql.Node]], AstNodeContext],
    ] = {}
    blank_value = AstNodeContext(node=ast.Name(""), type="String", dependencies=[])

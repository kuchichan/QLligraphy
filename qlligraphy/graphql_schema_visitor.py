import ast
from typing import Callable, Dict, Optional

import graphql

from .visitor import Visitor


class GraphQLSchemaVisitor(Visitor[graphql.Node, ast.AST]):
    type_to_func_map: Dict[
        type[graphql.Node],
        Callable[["Visitor", graphql.Node, Optional[graphql.Node]], ast.AST],
    ] = {}
    blank_value = ast.Name("")

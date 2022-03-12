import ast
from typing import Callable, Dict, Optional

import graphql

from .base.visitor import Visitor
from .ast_node_context import AstNodeContext


class GraphQLSchemaVisitor(Visitor[graphql.Node, AstNodeContext]):
    type_to_func_map: Dict[
        type[graphql.Node],
        Callable[["Visitor", graphql.Node, Optional[graphql.Node]], AstNodeContext],
    ] = {}
    blank_value = AstNodeContext(node=ast.Name(""), type="String", dependencies=[])

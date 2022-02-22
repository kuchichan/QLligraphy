import ast

import graphql

from .visitor import Visitor


class GraphQLSchemaVisitor(Visitor[graphql.Node, ast.AST]):
    blank_value = ast.Name("")

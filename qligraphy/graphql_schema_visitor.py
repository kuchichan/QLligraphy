from ast import AST
from typing import Final
from graphql.language.ast import (
    FieldDefinitionNode,
    ListTypeNode,
    NameNode,
    NamedTypeNode,
    Node,
    NonNullTypeNode,
)

from .visitor import Visitor
from .py_ast_builders import build_annotation_assignment, build_name, build_subscript

OPTIONAL: Final[str] = "Optional"
LIST: Final[str] = "List"

graph_ql_schema_visitor = Visitor[Node]()


@graph_ql_schema_visitor.register(FieldDefinitionNode)
def visit_field_definition_node(visitor: Visitor[Node], node: FieldDefinitionNode):
    target = visitor.visit(node.name)
    annotation = visitor.visit(node.type)

    if not isinstance(node.type, NonNullTypeNode):
        annotation = build_subscript(OPTIONAL, annotation)

    return build_annotation_assignment(target, annotation)


@graph_ql_schema_visitor.register(NonNullTypeNode)
def visit_non_null_type_node(visitor, node: NonNullTypeNode):
    return visitor.visit(node.type)


@graph_ql_schema_visitor.register(NamedTypeNode)
def visit_named_type_node(visitor, node: NamedTypeNode):
    return visitor.visit(node.name)


@graph_ql_schema_visitor.register(ListTypeNode)
def visit_list_type_node(visitor, node: ListTypeNode):
    slice_ = visitor.visit(node.type)
    return build_subscript(LIST, slice_=slice_)


@graph_ql_schema_visitor.register(NameNode)
def visit_name_node(_: Visitor, node: NameNode):
    return build_name(name=node.value)

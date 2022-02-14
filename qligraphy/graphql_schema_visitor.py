from ast import AST
from typing import Final
from graphql.language.ast import (
    FieldDefinitionNode,
    ListTypeNode,
    NameNode,
    NamedTypeNode,
    Node,
    NonNullTypeNode,
    ObjectTypeDefinitionNode,
)

from .visitor import Visitor
from .py_ast_builders import (
    ClassBuilder,
    build_annotation_assignment,
    build_name,
    build_subscript,
    make_pydantic_basemodel,
)

OPTIONAL: Final[str] = "Optional"
LIST: Final[str] = "List"

graphql_schema_visitor = Visitor[Node]()


@graphql_schema_visitor.register(ObjectTypeDefinitionNode)
def visit_type_definition_node(visitor: Visitor[Node], node: ObjectTypeDefinitionNode):
    class_body = [visitor.visit(field) for field in node.fields]
    builder = ClassBuilder(name=visitor.visit(node.name))
    class_def = make_pydantic_basemodel(body=class_body, builder=builder)
    return class_def


@graphql_schema_visitor.register(FieldDefinitionNode)
def visit_field_definition_node(visitor: Visitor[Node], node: FieldDefinitionNode):
    target = visitor.visit(node.name)
    annotation = visitor.visit(node.type)

    if not isinstance(node.type, NonNullTypeNode):
        annotation = build_subscript(OPTIONAL, annotation)

    return build_annotation_assignment(target, annotation)


@graphql_schema_visitor.register(NonNullTypeNode)
def visit_non_null_type_node(visitor, node: NonNullTypeNode):
    return visitor.visit(node.type)


@graphql_schema_visitor.register(NamedTypeNode)
def visit_named_type_node(visitor, node: NamedTypeNode):
    return visitor.visit(node.name)


@graphql_schema_visitor.register(ListTypeNode)
def visit_list_type_node(visitor, node: ListTypeNode):
    slice_ = visitor.visit(node.type)
    return build_subscript(LIST, slice_=slice_)


@graphql_schema_visitor.register(NameNode)
def visit_name_node(_: Visitor[Node], node: NameNode):
    return build_name(name=node.value)

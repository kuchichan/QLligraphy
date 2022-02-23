from ast import Name, AST, AnnAssign, ClassDef, stmt, Subscript
from typing import Dict, Final, List, Optional, Union, cast

from graphql.language.ast import (
    DocumentNode,
    EnumTypeDefinitionNode,
    EnumValueDefinitionNode,
    FieldDefinitionNode,
    ListTypeNode,
    NameNode,
    NamedTypeNode,
    Node,
    NonNullTypeNode,
    ObjectTypeDefinitionNode,
)

from .visitor import Visitor
from .graphql_schema_visitor import GraphQLSchemaVisitor
from .py_ast_builders import (
    ClassBuilder,
    build_annotation_assignment,
    build_name,
    build_subscript,
    make_enum_class,
    make_pydantic_basemodel,
    make_pydantic_module,
)

OPTIONAL: Final[str] = "Optional"
LIST: Final[str] = "List"
GQL_TO_PY_SIMPLE_TYPE_MAP: Final[Dict[str, str]] = {
    "String": "str",
    "ID": "str",
    "Integer": "int",
    "Boolean": "bool",
    "Float": "float",
}


@GraphQLSchemaVisitor.register(DocumentNode)
def visit_document_node(
    visitor: Visitor[Node, AST], node: DocumentNode, _: Optional[Node] = None
):
    definitons = cast(
        List[stmt], [visitor.visit(definition, node) for definition in node.definitions]
    )

    return make_pydantic_module(definitons)


@GraphQLSchemaVisitor.register(ObjectTypeDefinitionNode)
def visit_type_definition_node(
    visitor: Visitor[Node, AST],
    node: ObjectTypeDefinitionNode,
    _: Optional[Node] = None,
) -> ClassDef:
    class_body = cast(List[stmt], [visitor.visit(field, node) for field in node.fields])

    builder = ClassBuilder(name=node.name.value)
    class_def = make_pydantic_basemodel(body=class_body, builder=builder)

    return class_def


@GraphQLSchemaVisitor.register(EnumTypeDefinitionNode)
def visit_enum_type_definition_node(
    visitor: Visitor[Node, AST], node: EnumTypeDefinitionNode, _: Optional[Node]
):
    class_body = cast(
        List[Name], [visitor.visit(enum_val, node) for enum_val in node.values]
    )

    builder = ClassBuilder(name=node.name.value)
    class_def = make_enum_class(class_body, builder=builder)

    return class_def


@GraphQLSchemaVisitor.register(FieldDefinitionNode)
def visit_field_definition_node(
    visitor: Visitor[Node, AST], node: FieldDefinitionNode, _: Optional[Node] = None
) -> AnnAssign:
    target = visitor.visit(node.name, node)
    annotation: Union[AST, Subscript] = visitor.visit(node.type, node)

    return build_annotation_assignment(target, annotation)


@GraphQLSchemaVisitor.register(EnumValueDefinitionNode)
def visit_enum_value_definition_node(
    visitor: Visitor[Node, AST], node: FieldDefinitionNode, _: Optional[Node] = None
):
    return visitor.visit(node.name, node)


@GraphQLSchemaVisitor.register(NonNullTypeNode)
def visit_non_null_type_node(
    visitor: Visitor[Node, AST], node: NonNullTypeNode, _: Optional[Node] = None
):
    return visitor.visit(node.type, node)


@GraphQLSchemaVisitor.register(NamedTypeNode)
def visit_named_type_node(
    visitor: Visitor[Node, AST], node: NamedTypeNode, ancestor: Optional[Node] = None
):
    visited = visitor.visit(node.name, node)

    if isinstance(ancestor, NonNullTypeNode):
        return visited

    return build_subscript(build_name(OPTIONAL), visited)


@GraphQLSchemaVisitor.register(ListTypeNode)
def visit_list_type_node(
    visitor: Visitor[Node, AST], node: ListTypeNode, ancestor: Optional[Node] = None
) -> Subscript:
    slice_ = visitor.visit(node.type, node)
    list_subscript = build_subscript(build_name(LIST), slice_=slice_)

    if isinstance(ancestor, NonNullTypeNode):
        return list_subscript

    return build_subscript(build_name(OPTIONAL), list_subscript)


@GraphQLSchemaVisitor.register(NameNode)
def visit_name_node(
    _: Visitor[Node, AST], node: NameNode, __: Optional[Node] = None
) -> Name:
    name = GQL_TO_PY_SIMPLE_TYPE_MAP.get(node.value, node.value)
    return build_name(name=name)

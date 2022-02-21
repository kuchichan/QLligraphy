from ast import Name, AST, AnnAssign, ClassDef, stmt, Subscript
from typing import Dict, Final, List, Optional, Union, cast
from graphql.language.ast import (
    DocumentNode,
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
    make_pydantic_module,
)

OPTIONAL: Final[str] = "Optional"
LIST: Final[str] = "List"
GQL_TO_PY_SIMPLE_TYPE_MAP: Final[Dict[str, str]] = {
    "String": "str",
    "ID": "str",
    "Integer": "int",
}

graphql_schema_visitor = Visitor[Node, AST](blank_value=Name(""))


@graphql_schema_visitor.register(DocumentNode)
def visit_document_node(
    visitor: Visitor[Node, AST], node: DocumentNode, _: Optional[Node] = None
):

    definitons = cast(
        List[stmt], [visitor.visit(definition, node) for definition in node.definitions]
    )
    return make_pydantic_module(definitons)


@graphql_schema_visitor.register(ObjectTypeDefinitionNode)
def visit_type_definition_node(
    visitor: Visitor[Node, AST],
    node: ObjectTypeDefinitionNode,
    _: Optional[Node] = None,
) -> ClassDef:
    class_body = cast(List[stmt], [visitor.visit(field, node) for field in node.fields])

    builder = ClassBuilder(name=node.name.value)
    class_def = make_pydantic_basemodel(body=class_body, builder=builder)
    return class_def


@graphql_schema_visitor.register(FieldDefinitionNode)
def visit_field_definition_node(
    visitor: Visitor[Node, AST], node: FieldDefinitionNode, _: Optional[Node] = None
) -> AnnAssign:
    target = visitor.visit(node.name, node)
    annotation: Union[AST, Subscript] = visitor.visit(node.type, node)

    return build_annotation_assignment(target, annotation)


@graphql_schema_visitor.register(NonNullTypeNode)
def visit_non_null_type_node(
    visitor: Visitor[Node, AST], node: NonNullTypeNode, _: Optional[Node] = None
):
    return visitor.visit(node.type, node)


@graphql_schema_visitor.register(NamedTypeNode)
def visit_named_type_node(
    visitor: Visitor[Node, AST], node: NamedTypeNode, ancestor: Optional[Node] = None
):
    visited = visitor.visit(node.name, node)

    if isinstance(ancestor, NonNullTypeNode):
        return visited

    return build_subscript(build_name(OPTIONAL), visited)


@graphql_schema_visitor.register(ListTypeNode)
def visit_list_type_node(
    visitor: Visitor[Node, AST], node: ListTypeNode, ancestor: Optional[Node] = None
):
    slice_ = visitor.visit(node.type, node)
    list_subscript = build_subscript(build_name(LIST), slice_=slice_)

    if isinstance(ancestor, NonNullTypeNode):
        return list_subscript

    return build_subscript(build_name(OPTIONAL), list_subscript)


@graphql_schema_visitor.register(NameNode)
def visit_name_node(
    _: Visitor[Node, AST], node: NameNode, __: Optional[Node] = None
) -> Name:
    name = GQL_TO_PY_SIMPLE_TYPE_MAP.get(node.value, node.value)
    return build_name(name=name)

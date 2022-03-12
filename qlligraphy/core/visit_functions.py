from ast import Name, AST, stmt
from typing import List, Optional, cast

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

from .base.visitor import Visitor
from .graphql_schema_visitor import GraphQLSchemaVisitor
from .constants import GQL_TO_PY_SIMPLE_TYPE_MAP, LIST, OPTIONAL
from .ast_node_context import AstNodeContext, Imports, topological_sort
from .py_ast_builders import (
    ClassBuilder,
    build_annotation_assignment,
    build_name,
    build_subscript,
    make_enum_class,
    make_pydantic_basemodel,
    make_pydantic_module,
)


@GraphQLSchemaVisitor.register(DocumentNode)
def visit_document_node(
    visitor: Visitor[Node, AstNodeContext], node: DocumentNode, _: Optional[Node] = None
):
    definitions_ctx = [
        visitor.visit(definition, node) for definition in node.definitions
    ]
    definition_map = {definition.type: definition for definition in definitions_ctx}
    for definition in definitions_ctx:
        definition.build_dependencies(definition_map)

    sorted_definitons = topological_sort(definitions_ctx)
    imports = {import_ for ctx in definitions_ctx for import_ in ctx.imports}

    return AstNodeContext(
        node=make_pydantic_module(
            cast(List[stmt], [ctx.node for ctx in sorted_definitons]), imports
        ),
        type="",
    )


@GraphQLSchemaVisitor.register(ObjectTypeDefinitionNode)
def visit_type_definition_node(
    visitor: Visitor[Node, AstNodeContext],
    node: ObjectTypeDefinitionNode,
    _: Optional[Node] = None,
) -> AstNodeContext:
    ctx_list = [visitor.visit(field, node) for field in node.fields]
    types = [
        field.type
        for field in ctx_list
        if field.type not in GQL_TO_PY_SIMPLE_TYPE_MAP.values()
    ]

    body = cast(List[stmt], [ctx.node for ctx in ctx_list])
    imports = {import_ for ctx in ctx_list for import_ in ctx.imports}
    imports.add(Imports.PYDANTIC)
    name = node.name.value

    builder = ClassBuilder(name=name)
    class_def = make_pydantic_basemodel(body=body, builder=builder)

    return AstNodeContext(
        node=class_def, type=name, field_types=types, imports=frozenset(imports)
    )


@GraphQLSchemaVisitor.register(EnumTypeDefinitionNode)
def visit_enum_type_definition_node(
    visitor: Visitor[Node, AstNodeContext],
    node: EnumTypeDefinitionNode,
    _: Optional[Node],
) -> AstNodeContext:
    ctx_list = [visitor.visit(enum_val, node) for enum_val in node.values]
    class_body = cast(List[Name], [ctx.node for ctx in ctx_list])
    imports = {import_ for ctx in ctx_list for import_ in ctx.imports}
    imports.add(Imports.ENUM)
    name = node.name.value

    builder = ClassBuilder(name=name)
    class_def = make_enum_class(class_body, builder=builder)

    return AstNodeContext(node=class_def, type=name, imports=frozenset(imports))


@GraphQLSchemaVisitor.register(FieldDefinitionNode)
def visit_field_definition_node(
    visitor: Visitor[Node, AstNodeContext],
    node: FieldDefinitionNode,
    _: Optional[Node] = None,
) -> AstNodeContext:
    target: AstNodeContext = visitor.visit(node.name, node)
    annotation: AstNodeContext = visitor.visit(node.type, node)
    imports = target.imports.union(annotation.imports)

    return AstNodeContext(
        node=build_annotation_assignment(target.node, annotation.node),
        type=annotation.type,
        imports=imports,
    )


@GraphQLSchemaVisitor.register(EnumValueDefinitionNode)
def visit_enum_value_definition_node(
    visitor: Visitor[Node, AST], node: FieldDefinitionNode, _: Optional[Node] = None
):
    return visitor.visit(node.name, node)


@GraphQLSchemaVisitor.register(NonNullTypeNode)
def visit_non_null_type_node(
    visitor: Visitor[Node, AstNodeContext],
    node: NonNullTypeNode,
    _: Optional[Node] = None,
) -> AstNodeContext:
    return visitor.visit(node.type, node)


@GraphQLSchemaVisitor.register(NamedTypeNode)
def visit_named_type_node(
    visitor: Visitor[Node, AstNodeContext],
    node: NamedTypeNode,
    ancestor: Optional[Node] = None,
) -> AstNodeContext:
    visited = visitor.visit(node.name, node)

    if isinstance(ancestor, NonNullTypeNode):
        return visited

    return AstNodeContext(
        node=build_subscript(build_name(OPTIONAL), visited.node),
        type=visited.type,
        imports=visited.imports.union([Imports.TYPING_OPTIONAL]),
    )


@GraphQLSchemaVisitor.register(ListTypeNode)
def visit_list_type_node(
    visitor: Visitor[Node, AstNodeContext],
    node: ListTypeNode,
    ancestor: Optional[Node] = None,
) -> AstNodeContext:
    ctx = visitor.visit(node.type, node)
    list_subscript = build_subscript(build_name(LIST), slice_=ctx.node)

    if isinstance(ancestor, NonNullTypeNode):
        return AstNodeContext(
            node=list_subscript,
            type=ctx.type,
            imports=ctx.imports.union([Imports.TYPING_LIST]),
        )

    return AstNodeContext(
        node=build_subscript(build_name(OPTIONAL), list_subscript),
        type=ctx.type,
        imports=ctx.imports.union([Imports.TYPING_OPTIONAL, Imports.TYPING_LIST]),
    )


@GraphQLSchemaVisitor.register(NameNode)
def visit_name_node(
    _: Visitor[Node, AstNodeContext], node: NameNode, __: Optional[Node] = None
) -> AstNodeContext:
    name = GQL_TO_PY_SIMPLE_TYPE_MAP.get(node.value, node.value)

    return AstNodeContext(node=build_name(name=name), type=name)

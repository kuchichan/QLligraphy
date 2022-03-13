from typing import Iterable, Set, Union, Any, List
from ast import (
    ClassDef,
    Constant,
    Pass,
    Name,
    Load,
    Store,
    AnnAssign,
    Assign,
    Subscript,
    AST,
    stmt,
    Module,
    ImportFrom,
    alias,
)

from qlligraphy.core.ast_node_context import Imports, IMPORTS_MAP

Context = Union[Load, Store]


class ClassBuilder:
    def __init__(self, name: str) -> None:
        self.class_def = ClassDef(
            name=name, decorator_list=[], bases=[], body=[Pass()], keywords=[]
        )

    def build_bases(self, base_names: Iterable[str]) -> None:
        for name in base_names:
            self.class_def.bases.append(build_name(name))

    def build_body(self, expressions: Iterable[stmt]) -> None:
        self.class_def.body = []

        for expr in expressions:
            self.class_def.body.append(expr)


def build_module(body: List[stmt]) -> Module:
    return Module(body=body)


def build_subscript_assignment(target: Name, value: Name, slice_: AST) -> AnnAssign:
    return build_annotation_assignment(target, build_subscript(value, slice_))


def build_name_assigment(target: Name, value: str) -> AnnAssign:
    return build_annotation_assignment(target, build_name(value))


def build_annotation_assignment(target: AST, annotation: Any) -> AnnAssign:
    return AnnAssign(target, annotation, simple=1)


def build_subscript(value: Name, slice_: AST) -> Subscript:
    return Subscript(value=value, slice=slice_)


def build_name(name: str, ctx: Context = Load()) -> Name:
    return Name(id=name, ctx=ctx)


def make_pydantic_basemodel(body: Iterable[stmt], builder: ClassBuilder) -> ClassDef:
    builder.build_bases(["BaseModel"])
    builder.build_body(body)

    return builder.class_def


def make_scalar_definition(builder: ClassBuilder):
    pass


def make_enum_class(targets: Iterable[Name], builder: ClassBuilder) -> ClassDef:
    builder.build_bases(["str", "Enum"])
    body = [
        Assign(targets=[target], value=Constant(value=target.id.upper()))
        for target in targets
    ]

    builder.build_body(body)

    return builder.class_def


def make_pydantic_module(body: List[stmt], imports: Set[Imports]) -> Module:
    import_list: List[stmt] = []
    for import_ in imports:
        from_, to_ = IMPORTS_MAP[import_]
        import_list.append(ImportFrom(module=from_, names=[alias(name=to_)], level=0))

    return build_module(body=import_list + body)

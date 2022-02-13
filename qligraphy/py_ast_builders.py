from typing import Iterable, Union, Any
from ast import ClassDef, Pass, Name, Load, Store, AnnAssign, Expr, Subscript

Context = Union[Load, Store]


class ClassBuilder:
    def __init__(self, name: str) -> None:
        self.class_def = ClassDef(
            name=name, decorator_list=[], bases=[], body=Pass(), keywords=[]
        )

    def build_bases(self, base_names: Iterable[str]) -> None:
        for name in base_names:
            self.class_def.bases.append(build_name(name))

    def build_body(self, expressions: Iterable[Expr]) -> None:
        for expr in expressions:
            self.class_def.body.append(expr)


def build_subscript_assignment(target: str, value: str, slice_: str) -> AnnAssign:
    return build_annotation_assignment(target, build_subscript(value, slice_))


def build_name_assigment(target: str, value: str) -> AnnAssign:
    return build_annotation_assignment(target, build_name(value))


def build_annotation_assignment(target: str, annotation: Any) -> AnnAssign:
    build_target = build_name(target, ctx=Store())
    return AnnAssign(build_target, annotation, simple=1)


def build_subscript(value: str, slice_: str) -> Subscript:
    return Subscript(value=build_name(value), slice=build_name(slice_))


def build_name(name: str, ctx: Context = Load()) -> Name:
    return Name(name=name, ctx=ctx)

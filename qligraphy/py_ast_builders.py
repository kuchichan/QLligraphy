from typing import Iterable, Union

from ast import ClassDef, Pass, Name, Load, Store

Context = Union[Load, Store]


def build_name(name: str, ctx: Context = Load()) -> Name:
    return Name(name=name, ctx=ctx)


class ClassBuilder:
    def __init__(self, name: str) -> None:
        self.class_def = ClassDef(
            name=name, decorator_list=[], bases=[], body=Pass(), keywords=[]
        )

    def build_bases(self, base_names: Iterable[str]) -> None:
        for name in base_names:
            self.class_def.bases.append(build_name(name))

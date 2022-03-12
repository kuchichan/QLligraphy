from typing import Callable, Dict, Generic, TypeVar, Type, Optional

T = TypeVar("T")  # pylint: disable=invalid-name
K = TypeVar("K")  # pylint: disable=invalid-name


class Visitor(Generic[T, K]):
    type_to_func_map: Dict[type[T], Callable[["Visitor", T, Optional[T]], K]] = {}
    blank_value: K

    def visit(self, node: T, ancestor: Optional[T] = None) -> K:
        function = self.type_to_func_map.get(type(node), Visitor[T, K].blank_visit)
        return function(self, node, ancestor)

    def blank_visit(self, *_: Optional[T]) -> K:  # type: ignore
        return self.blank_value

    @classmethod
    def register(cls, node_type: Type[T]):
        def outer(func):
            cls.type_to_func_map[node_type] = func

            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            return inner

        return outer

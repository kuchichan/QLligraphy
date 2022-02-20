from typing import Callable, Dict, Generic, TypeVar, Type, Optional

T = TypeVar("T")  # pylint: disable=invalid-name
K = TypeVar("K")  # pylint: disable=invalid-name


class Visitor(Generic[T, K]):
    def __init__(self, neutral_element: K):
        self._neutral_element: K = neutral_element
        self._type_to_func_map: Dict[
            type[T], Callable[["Visitor", T, Optional[T]], K]
        ] = {}

    def visit(self, node: T, ancestor: Optional[T] = None) -> K:
        function = self._type_to_func_map.get(type(node), Visitor[T, K].blank_visit)
        return function(self, node, ancestor)

    def blank_visit(self, *_: Optional[T]) -> K:
        return self._neutral_element

    def register(self, node_type: Type[T]):
        def outer(func):
            self._type_to_func_map[node_type] = func

            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            return inner

        return outer

from typing import Callable, Dict, Generic, TypeVar, Type

T = TypeVar("T")
K = TypeVar("K")


class Visitor(Generic[T, K]):
    def __init__(self, neutral_element: K):
        self._neutral_element: K = neutral_element
        self._type_to_func_map: Dict[type[T], Callable[["Visitor", T], K]] = dict()

    def visit(self, node: T) -> K:
        function = self._type_to_func_map.get(type(node), Visitor[T, K]._blank_visit)
        return function(self, node)

    def _blank_visit(self, _: T) -> K:
        return self._neutral_element

    def register(self, node_type: Type[T]):
        def outer(func):
            self._type_to_func_map[node_type] = func

            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            return inner

        return outer

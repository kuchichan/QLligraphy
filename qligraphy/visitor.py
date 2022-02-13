from typing import Callable, Dict, Generic, Any, TypeVar, Type

T = TypeVar("T")
K = TypeVar("K")


class Visitor(Generic[T]):
    def __init__(self):
        self._type_to_func_map: Dict[T, Callable[["Visitor", T], Any]] = dict()

    def visit(self, node: T) -> Any:
        function = self._type_to_func_map.get(type(node), Visitor._blank_visit)
        return function(self, node)

    def _blank_visit(self, _):
        pass

    def register(self, node_type: Type[T]):
        def outer(func):
            self._type_to_func_map[node_type] = func

            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            return inner

        return outer

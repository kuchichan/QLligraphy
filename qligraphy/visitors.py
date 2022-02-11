from typing import Callable, Dict, Any, TypeVar, Type

T = TypeVar("T")


class Visitor:
    def __init__(self):
        self._type_to_func_map: Dict[Any, Callable[["Visitor", Any], Any]] = dict()

    def visit(self, node: Any) -> Any:
        function = self._type_to_func_map.get(type(node), Visitor._blank_visit)
        return function(self, node)

    def _blank_visit(self, _): 
        pass

    def register(self, node_type):
        def outer(func):
            self._type_to_func_map[node_type] = func

            def inner(*args, **kwargs):
                return func(*args, **kwargs)

            return inner

        return outer

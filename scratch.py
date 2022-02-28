from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class Node:
    value: Any
    deps: List["Node"] = field(default_factory=list)
    status = "not_resolved"


def topological_sort(nodes: List[Node]):
    sorted_list = []
    stack = nodes[:]

    while stack:
        considered_node = stack.pop()
        if considered_node.status == "visited":
            continue

        if considered_node.status == "resolved" or not considered_node.deps:
            sorted_list.append(considered_node)
            considered_node.status = "visited"
        else:
            considered_node.status = "resolved"
            stack.append(considered_node)
            for dependency in considered_node.deps:
                stack.append(dependency)

    return sorted_list


node_1 = Node(value=5, deps=[])
node_2 = Node(value=10, deps=[node_1])

node_3 = Node(value=15, deps=[node_1, node_2])
node_4 = Node(value=20, deps=[node_1, node_2, node_3])
node_5 = Node(value=25, deps=[node_4])

node_list = [node_5, node_1, node_2, node_3, node_4]

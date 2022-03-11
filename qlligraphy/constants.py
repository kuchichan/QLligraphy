from typing import Final, Dict

GQL_TO_PY_SIMPLE_TYPE_MAP: Final[Dict[str, str]] = {
    "String": "str",
    "ID": "str",
    "Integer": "int",
    "Boolean": "bool",
    "Float": "float",
}
OPTIONAL: Final[str] = "Optional"
LIST: Final[str] = "List"

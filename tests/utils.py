from textwrap import dedent


def shrink_python_source_code(source_code: str) -> str:
    return dedent(source_code).strip()

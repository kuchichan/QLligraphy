import argparse
import pathlib
from typing import Optional, cast

import black
import isort
from astunparse import unparse
from graphql import parse

from .core import visit_functions  # pylint: disable=unused-import
from .core.graphql_schema_visitor import GraphQLSchemaVisitor


def app():
    schema_visitor = GraphQLSchemaVisitor()
    args = parse_args()
    gql_path = cast(pathlib.Path, make_path(args.schemapath))
    output_path = make_path(args.output)
    schema = read_schema(gql_path)
    python_ast = schema_visitor.visit(parse(schema)).node
    python_source = black.format_str(isort.code(unparse(python_ast)), mode=black.Mode())
    write_to_output(python_source, output_path)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("schemapath", type=pathlib.Path)
    parser.add_argument("-o", "--output", type=pathlib.Path)

    return parser.parse_args()


def read_schema(gql_path: pathlib.Path):
    with open(gql_path, encoding="utf-8") as schema:
        data = schema.read()

    return data


def write_to_output(python_source, output_path):
    if not output_path:
        print(python_source)
        return

    with open(output_path, "w", encoding="utf-8") as output:
        output.write(python_source)


def make_path(path: Optional[pathlib.Path]):
    if path is None:
        return None
    return path if path.is_absolute() else pathlib.Path.cwd() / path

import pathlib

import black
import click
import isort
from astunparse import unparse
from graphql import parse

from .core import visit_functions  # pylint: disable=unused-import
from .core.graphql_schema_visitor import GraphQLSchemaVisitor


@click.command()
@click.argument("schemapath", type=click.Path(exists=True))
@click.option("-o", "--output", "output", required=False, type=click.Path(exists=False))
def app(schemapath, output):
    schema_visitor = GraphQLSchemaVisitor()
    gql_path = make_path(pathlib.Path(schemapath))
    output_path = output

    if output is not None:
        output_path = make_path(pathlib.Path(output))

    schema = read_schema(gql_path)
    python_ast = schema_visitor.visit(parse(schema)).node
    python_source = black.format_str(isort.code(unparse(python_ast)), mode=black.Mode())
    write_to_output(python_source, output_path)


def read_schema(gql_path: pathlib.Path):
    with open(gql_path, encoding="utf-8") as schema:
        data = schema.read()

    return data


def write_to_output(python_source, output_path):
    if not output_path:
        click.echo(python_source)
        return

    with open(output_path, "w", encoding="utf-8") as output:
        output.write(python_source)


def make_path(path: pathlib.Path):
    return path if path.is_absolute() else pathlib.Path.cwd() / path

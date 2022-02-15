from astunparse import unparse
from graphql import parse

from qlligraphy.graphql_schema_visitor import graphql_schema_visitor


def test_gql_schema_visior_creates_class_def_from_object_definition():
    class_character_graphql_schema = """
      type Character {
      name: String!
      appearsIn: [Episode!]!
    }
    """

    class_character_source_code = """

class Character(BaseModel):
    name: str
    appearsIn: List[Episode]
"""

    gql_ast = parse(class_character_graphql_schema)
    class_def = graphql_schema_visitor.visit(gql_ast.definitions[0])

    assert unparse(class_def) == class_character_source_code

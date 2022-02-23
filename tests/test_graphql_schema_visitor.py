from astunparse import unparse
from graphql import parse

from qlligraphy.graphql_schema_visitor import GraphQLSchemaVisitor
from qlligraphy import visit_functions  # pylint: disable=unused-import

from .utils import shrink_python_source_code


def test_gql_schema_visior_creates_class_def_from_object_definition():
    graphql_schema_visitor = GraphQLSchemaVisitor()
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

    assert shrink_python_source_code(unparse(class_def)) == shrink_python_source_code(
        class_character_source_code
    )


def test_gql_schema_visitor_creates_class_def_with_optional():
    graphql_schema_visitor = GraphQLSchemaVisitor()
    class_character_graphql_schema = """
    type Character {
      name: String
      appearsIn: [Episode]
    }
    """

    class_character_source_code = """
    class Character(BaseModel):
        name: Optional[str]
        appearsIn: Optional[List[Optional[Episode]]]
     """

    gql_ast = parse(class_character_graphql_schema)
    class_def = graphql_schema_visitor.visit(gql_ast.definitions[0])

    assert shrink_python_source_code(unparse(class_def)) == shrink_python_source_code(
        class_character_source_code
    )


def test_gql_schema_visitor_module_with_imports():
    graphql_schema_visitor = GraphQLSchemaVisitor()
    enum_episode_graphql_schema = """
    enum Episode {
      NEWHOPE
      EMPIRE
      JEDI
    }

    type Character {
      name: String
      appearsIn: [Episode]
    }
    """

    enum_episode_source_code = """
    from pydantic import BaseModel

    class Episode(str, Enum):
        NEWHOPE = 'NEWHOPE'
        EMPIRE = 'EMPIRE'
        JEDI = 'JEDI'

    class Character(BaseModel):
        name: Optional[str]
        appearsIn: Optional[List[Optional[Episode]]]
    """

    gql_ast = parse(enum_episode_graphql_schema)
    enum_def = graphql_schema_visitor.visit(gql_ast)

    assert shrink_python_source_code(unparse(enum_def)) == shrink_python_source_code(
        enum_episode_source_code
    )

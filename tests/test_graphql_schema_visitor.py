from astunparse import unparse
from graphql import parse

from qlligraphy.graphql_schema_visitor import graphql_schema_visitor
from tests.utils import shrink_python_source_code


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

    assert shrink_python_source_code(unparse(class_def)) == shrink_python_source_code(
        class_character_source_code
    )


def test_gql_schema_visitor_creates_class_def_with_optional():
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
    enum_episode_graphql_schema = """
    type Character {
      name: String
      appearsIn: [Episode]
    }
     
    enum Episode {
        NEWHOPE
        EMPIRE
        JEDI
     }
    """

    enum_episode_source_code = """
    from pydantic import BaseModel
 
    class Character(BaseModel):
        name: Optional[str]
        appearsIn: Optional[List[Optional[Episode]]]
    """

    gql_ast = parse(enum_episode_graphql_schema)
    enum_def = graphql_schema_visitor.visit(gql_ast)

    assert shrink_python_source_code(unparse(enum_def)) == shrink_python_source_code(
        enum_episode_source_code
    )

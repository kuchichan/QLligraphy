from ast import parse
from astunparse import dump
from graphql import parse as parse_gql
from graphql.utilities.build_ast_schema import build_ast_schema 

gql_schema = """
enum Episode {
  NEWHOPE
  EMPIRE
  JEDI
}

enum LengthUnit {
  METER
} 


type Character {
  name: String!
  appearsIn: [Episode!]!
}

type Starship {
  id: ID!
  name: String!
  length(unit: LengthUnit = METER): Float
}

type Query {
  hero(episode: Episode): Character
}
"""

source_code = """
class Episode(str, Enum):
    NEWHOPE = auto()
    EMPIRE = auto()
    JEDI = auto()

class LengthUnit(Enum):
    METER = "METER"

class Character(BaseModel):
    name: str
    appears_in: List[Episode]

class A:
 pass 

class Starship(BaseModel):
    id: str
    name: str
    
    def length(self, unit: LengthUnit = LengthUnit.METER) -> float:
        ...
"""


dump(parse(source_code))
result = parse_gql(gql_schema)
schema = build_ast_schema(result)

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

![Master build](https://github.com/kuchichan/QLligraphy/actions/workflows/main.yml/badge.svg?branch=main)
# Qlligraphy. GraphQL Schema -> Pydantic models 

Qlligraphy is a simple CLI tool, that generates pydantic models based on graphQL schema. 

## Installation

``` shell
pip install qlligraphy
```

## Usage:
Consider the following schema written in `example.gql` 

``` graphQL 
enum Episode {
 NEWHOPE
 EMPIRE
 JEDI
}

type Character {
  name: String!
  appearsIn: [Episode]!
}
```

Running:

``` shell
qlligraphy example.gql -o example.py
```

Results in the following python file: 

``` python
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class Episode(str, Enum):
    NEWHOPE = "NEWHOPE"
    EMPIRE = "EMPIRE"
    JEDI = "JEDI"


class Character(BaseModel):
    name: str
    appearsIn: List[Optional[Episode]]

```

Please note: This package is still in WIP state.


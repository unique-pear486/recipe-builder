from __future__ import annotations
import re
from fractions import Fraction
from typing import Optional, List, Dict
from pydantic import BaseModel, validator
from pydantic.fields import ModelField
from pydantic_yaml import YamlModel

from mixed import MixedNumber

class Note(BaseModel):
    note: str


class Number(MixedNumber):
    "Generic number type, based on MixedNumber"
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        pass

    @classmethod
    def validate(cls, v):
        return cls(v)


class Amount(BaseModel):
    amount: Number
    unit: str


class Ingredient(BaseModel):
    amounts: List[Amount]
    processing: Optional[List[str]]
    notes: Optional[List[Note]]
    substitutions: Optional[List[Dict[str, 'Ingredient']]]


Ingredient.update_forward_refs()


class Step(BaseModel):
    step: str
    notes: Optional[List[Note]]


class Recipe(YamlModel):
    recipe_name: str
    ingredients: List[Dict[str, Ingredient]]
    source_url: Optional[str]
    yields: Optional[List[Dict[str, str]]]
    steps: List[Step]
    preparation_time: Optional[str]

    class Config():
        extra = 'forbid'

    @validator('yields')
    def num_of_yields_match(cls, v, values, **kwargs):
        for ingredient in values['ingredients']:
            name = list(ingredient.keys())[0]
            amounts = ingredient[name].amounts
            if len(amounts) != len(v):
                raise ValueError('Number of yields and ingredient amounts must'
                                 ' match\n'
                                 f'{name} {len(amounts)} != {len(v)} yields')


def main():
    r = Recipe.parse_file('eg.yaml')
    print(r)


if __name__ == '__main__':
    main()

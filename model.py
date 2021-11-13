from __future__ import annotations
from enum import Enum
from typing import Optional, List, Dict
from uuid import UUID
from pydantic import BaseModel, validator, HttpUrl
from pydantic_yaml import YamlModel

from mixed import MixedNumber


#
# Enums
#
class FanSpeed(str, Enum):
    off = 'Off'
    low = 'Low'
    high = 'High'


class TempUnit(str, Enum):
    celsius = 'C'
    fahrenheit = 'F'


#
# Custom Classes
#
class Number(MixedNumber):
    "Generic number type, based on MixedNumber"
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            pattern='^[+-]?[0-9]* [0-9]+/?[0-9]*$',
            examples=['1', '3/4', '2 1/3'],
        )

    @classmethod
    def validate(cls, v):
        return cls(v)


#
# BaseModels
#
class Note(BaseModel):
    note: str


class OvenTemp(BaseModel):
    amount: int
    unit: TempUnit


class Amount(BaseModel):
    amount: str
    unit: str


class Book(BaseModel):
    authors: Optional[List[str]]
    title: str
    isbn: Optional[str]
    notes: Optional[List[Note]]


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
    recipe_uuid: Optional[UUID]
    recipe_name: str
    ingredients: List[Dict[str, Ingredient]]
    source_url: Optional[str]
    yields: Optional[List[Dict[str, str]]]
    steps: List[Step]
    preparation_time: Optional[str]
    oven_fan: Optional[FanSpeed]
    oven_temp: Optional[OvenTemp]
    oven_time: Optional[str]
    source_book: Optional[Book]
    source_url: Optional[HttpUrl]
    source_authors: Optional[List[str]]

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
        return v


def main():
    from pathlib import Path
    recipes = Path('../recipe/')
    for filename in recipes.iterdir():
        if filename.suffix == '.yaml':
            print('===' + str(filename))
            r = Recipe.parse_file(filename)
            print(r)
    # r = Recipe.parse_file('eg.yaml')
    # print(r)


if __name__ == '__main__':
    main()

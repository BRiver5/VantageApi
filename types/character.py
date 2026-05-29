from FastAPI import FastAPI
from pydantic import BaseModel


class character(BaseModel):
    character_name: str
    race: race_info
    character_class: list[character_class]
    level: int
    experience_points: int
    proficiency_bonus: int
    hit_points: int
    max_hit_points: int
    temporary_hit_points: int
    armor_class: int
    shield: bool
    initiative_bonus: int
    inspiration: int

    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    saving_throw_strength: int
    saving_throw_dexterity: int
    saving_throw_constitution: int
    saving_throw_intelligence: int
    saving_throw_wisdom: int
    saving_throw_charisma: int

    skills: list[character_skill]


class character_skill(BaseModel):
    skill_name: str
    ability_source: str
    proficiency: bool
    expertise: bool
    passive_score: int
    bias_score: int


class class_info(BaseModel):
    class_name: str
    hit_dice: int
    saving_throw_proficiencies: list[str]
    armor_proficiencies: list[str]
    weapon_proficiencies: list[str]
    speed_bonus: int

class character_class(class_info):
    level: int

class race_info(BaseModel):
    race_name: str
    increase_ability_scores: dict[str, int]
    size: str
    speed: int
    darkvision: int
    languages: list[str]
    race_source: str
    max_age: int
    age_of_adulthood: int
    race_type: str
    flight_speed: int
    swimming_speed: int
    climbing_speed: int

    
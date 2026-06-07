from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .class_resource import character_class_resource
from .item import equipped_item


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
    background: int
    alignment: str
    player_id: UUID
    character_speed: int
    death_saves_success: int
    death_saves_failure: int

    personality_traits : list[str] | str
    ideals: list[str] | str
    bonds: list[str] | str
    flaws: list[str] | str
    age: int
    height: int
    weight: int
    eyes: str
    skin: str
    hair: str
    appearance: str
    avatar_url: str
    backstory: str
    treasures: list[UUID | str]



    features: list[UUID]
    extra_features: list[str]
    class_resources: list[character_class_resource] = Field(default_factory=list)


    languages: list[str]
    proficiences: list[UUID]
    extra_proficiences: list[str]



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

    caster_class: list[UUID]
    cantrips_amount: int
    prepared_spells: int
    spell_slots: dict[str, dict[int, int]] # {"class_name": {spell_level: spell_slots_amount}}
    spells: list[UUID]


    inventory: list[UUID | str]
    equipped_items: list[equipped_item] = Field(default_factory=list)

    copper: int
    silver: int
    electrum: int
    gold: int
    platinum: int


class CharacterResponse(character):
    id: UUID

    model_config = ConfigDict(from_attributes=True)



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
    class_source: UUID
    is_caster: bool
    default_spellcasting_ability: str | None
    class_resource_keys: list[str] = Field(default_factory=list)


class character_class(class_info):
    level: int

class race_info(BaseModel):
    race_name: str
    increase_ability_scores: dict[str, int]
    size: str
    speed: int
    darkvision: int
    languages: list[str]
    race_source: UUID
    max_age: int
    age_of_adulthood: int
    race_type: str
    flight_speed: int
    swimming_speed: int
    climbing_speed: int

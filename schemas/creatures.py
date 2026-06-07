from uuid import UUID
from typing import List, Literal

from pydantic import BaseModel


class Creature(BaseModel):
    is_npc: bool = False
    community_id: UUID | None = None

    name: str
    is_unique: bool
    description: str | None = None
    image_url: List[str] | None = None
    settings_id: UUID | None = None
    book_source_id: UUID | None = None
    size: Literal['Tiny', 'Small', 'Medium', 'Large', 'Huge', 'Gargantuan'] | None = None
    creature_type: str | None = None
    alignment: str | None = None
    ac: int
    ac_source: str | None = None
    hp: int
    hp_formula: str | None = None
    speed: int | None = None
    flight_speed: int | None = None
    swim_speed: int | None = None
    burrow_speed: int | None = None
    climb_speed: int | None = None

    strenght: int | None = None
    dexterity: int | None = None
    constitution: int | None = None
    intelligence: int | None = None
    wisdom: int | None = None
    charisma: int | None = None

    saving_throws: dict[str, int] | None = None

    skills: dict[str, int] | None = None
    damage_imunities: List[str] | None = None
    damage_resistances: List[str] | None = None
    damage_vulnerabilities: List[str] | None = None
    condition_imunities: List[str] | None = None

    night_vision: int | None = None
    blind_vision: int | None = None
    true_vision: int | None = None
    languages: List[str] | None = None
    can_speak: bool | None = None
    challenge_rating: float | None = None
    proficiency_bonus: int | None = None
    area_of_living: List[str] | None = None
    features: List[dict[str, str]] | None = None
    
    actions: List[dict[str, str]] | None = None
    actions_description: str | None = None

    legendary_actions: List[dict[str, str]] | None = None
    legendary_description: str | None = None

    mythical_actions: List[dict[str, str]] | None = None
    mythical_description: str | None = None

    creature_description: str | None = None

    image_gallery: List[str] | None = None
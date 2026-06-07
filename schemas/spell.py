from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class spell_components(BaseModel):
    verbal: bool
    somatic: bool
    material: bool


class spell(BaseModel):
    spell_name: str
    spell_level: int  # 0 = заговор
    school: str
    casting_time: str
    range: str
    components: spell_components
    material_components: str | None
    duration: str
    concentration: bool
    ritual: bool
    description: str
    higher_levels: str | None
    available_classes: list[str]
    available_races: list[str]
    available_subclasses: list[str]
    spellcasting_ability: str | None
    spell_source: UUID


class SpellResponse(spell):
    id: UUID

    model_config = ConfigDict(from_attributes=True)

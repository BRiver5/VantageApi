from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from .effects import functional_effect


class weapon_details(BaseModel):
    damage_dice: str
    damage_type: str
    weapon_category: str
    weapon_properties: list[str]
    range_normal: int | None
    range_long: int | None


class armor_details(BaseModel):
    armor_class: int
    armor_category: str
    dex_modifier_cap: int | None
    stealth_disadvantage: bool
    strength_requirement: int | None


class item(BaseModel):
    item_name: str
    item_type: str
    rarity: str
    attunement_required: bool
    weight: float
    cost_copper: int
    description: str
    item_source: UUID
    weapon: weapon_details | None
    armor: armor_details | None
    equipped_effects: list[functional_effect] = Field(default_factory=list)


class equipped_item(BaseModel):
    """Экипировка на персонаже (слот + ссылка на предмет)."""
    item_ref: UUID | str
    slot: str
    is_attuned: bool = False

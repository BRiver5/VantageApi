from uuid import UUID

from pydantic import BaseModel, Field

from .effects import functional_effect
from .item import armor_details as ArmorDetailsSchema, weapon_details as WeaponDetailsSchema


class ItemResponse(BaseModel):
    id: UUID
    item_name: str
    item_type: str
    rarity: str
    attunement_required: bool
    weight: float
    cost_copper: int
    description: str
    item_source: UUID
    item_image_id: int | None = None
    item_image_url: str | None = None
    weapon_details: WeaponDetailsSchema | None = None
    armor_details: ArmorDetailsSchema | None = None
    equipped_effects: list[functional_effect] = Field(default_factory=list)
    tool_category: str | None = None
    item_image_gallery: list[str] | None = None

    class Config:
        from_attributes = True

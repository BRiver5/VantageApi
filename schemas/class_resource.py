from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from .effects import functional_effect

# Тип классового ресурса
ClassResourceKind = Literal[
    "uses",        # ярость, дикий облик, проведение энергии
    "points",      # ци, очки чародейства, очки чар
    "pool",        # лечение ладонями (пул HP)
    "collection",  # воззвания, метамагия, манёвры, наставления
]

RechargeKind = Literal[
    "short_rest",
    "long_rest",
    "dawn",
    "none",
]

ScalingKind = Literal["table", "formula", "fixed"]


class level_scaling_rule(BaseModel):
    """
    Как вычислить максимум от суммарного уровня класса.
    table: {уровень_класса: значение}, берётся наибольшее подходящее
    formula: "level", "level//2", "proficiency_bonus" — ключ формулы
    fixed: константа
    """
    kind: ScalingKind
    table: dict[int, int] | None = None
    formula: str | None = None
    fixed: int | None = None


class collection_entry(BaseModel):
    """Элемент коллекции: воззвание, метамагия, манёвр, наставление барда…"""
    entry_name: str
    entry_source: UUID
    level_required: int
    description: str
    effects: list[functional_effect] = Field(default_factory=list)
    prerequisite_entries: list[UUID] = Field(default_factory=list)


class class_resource_template(BaseModel):
    """
    Шаблон классового ресурса в каталоге (привязан к class_source).
    Примеры resource_key: rage, ki, eldritch_invocations, sorcery_points,
    channel_divinity, bardic_inspiration, lay_on_hands, superiority_dice.
    """
    resource_key: str
    resource_name: str
    class_source: UUID
    kind: ClassResourceKind
    description: str
    recharge: RechargeKind | None = None
    level_scaling: level_scaling_rule | None = None
    collection_catalog: list[collection_entry] = Field(default_factory=list)
    collection_size_scaling: level_scaling_rule | None = None
    activation_effects: list[functional_effect] = Field(default_factory=list)
    passive_effects: list[functional_effect] = Field(default_factory=list)
    level_required: int = 1


# --- Состояние ресурса на персонаже (дискриминированный union по kind) ---


class _resource_base(BaseModel):
    resource_key: str
    class_source: UUID


class character_resource_uses(_resource_base):
    kind: Literal["uses"] = "uses"
    current: int
    maximum: int
    is_active: bool = False


class character_resource_points(_resource_base):
    kind: Literal["points"] = "points"
    current: int
    maximum: int


class character_resource_pool(_resource_base):
    kind: Literal["pool"] = "pool"
    current: int
    maximum: int


class character_resource_collection(_resource_base):
    kind: Literal["collection"] = "collection"
    selected_entries: list[UUID] = Field(default_factory=list)
    maximum: int


character_class_resource = Annotated[
    character_resource_uses
    | character_resource_points
    | character_resource_pool
    | character_resource_collection,
    Field(discriminator="kind"),
]

from __future__ import annotations

from uuid import UUID

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .effects import functional_effect

FeatureCategory = Literal[
    "standard",           # обычная фича (ASI, Extra Attack)
    "collection_entry",   # элемент коллекции (воззвание, метамагия)
]


class feature_option(BaseModel):
    """Вариант выбора (боевой стиль, метамагия и т.п.)."""
    option_name: str
    description: str
    effects: list[functional_effect]


class class_feature(BaseModel):
    """
    Шаблон фичи класса из каталога.
    character.features хранит UUID → feature_source.

    Для коллекций (воззвания, ци-способности как отдельные записи) используй
    category=collection_entry и resource_key, либо schemas.class_resource.collection_entry.
    """
    feature_name: str
    feature_source: UUID
    class_source: UUID
    level_required: int
    description: str
    category: FeatureCategory = "standard"
    resource_key: str | None = None
    is_optional: bool = False
    effects: list[functional_effect] = Field(default_factory=list)
    options: list[feature_option] | None = None
    prerequisite_features: list[UUID] = Field(default_factory=list)


class FeatureResponse(class_feature):
    id: UUID

    model_config = ConfigDict(from_attributes=True)

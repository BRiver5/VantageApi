from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from schemas.book import BookResponse
from schemas.campaign import Campaign
from services.ordering import chapters_to_content, normalize_campaign_content, CampaignResponse
from schemas.character import character as CharacterSchema, CharacterResponse
from schemas.class_resource import (
    class_resource_template as ClassResourceSchema,
    ClassResourceResponse,
)
from schemas.communities import Comunnity as CommunitySchema, CommunityResponse
from schemas.creatures import Creature as CreatureSchema, CreatureResponse
from schemas.feature import class_feature as FeatureSchema, FeatureResponse
from schemas.item import item as ItemSchema
from schemas.location import Location as LocationSchema, LocationResponse
from schemas.religion import Religion as ReligionSchema, ReligionResponse
from schemas.spell import spell as SpellSchema, SpellResponse
from schemas.termins import Termins as TerminsSchema, TerminsResponse


def _dump_list(items: list[BaseModel] | None) -> list[dict] | None:
    if items is None:
        return None
    return [item.model_dump(mode="json") for item in items]


def _dump_optional(model: BaseModel | None) -> dict | None:
    return model.model_dump(mode="json") if model else None


# --- Spell ---

def spell_to_orm(data: SpellSchema) -> dict[str, Any]:
    return {
        "spell_name": data.spell_name,
        "spell_level": data.spell_level,
        "school": data.school,
        "casting_time": data.casting_time,
        "range": data.range,
        "components": data.components.model_dump(mode="json"),
        "material_components": data.material_components,
        "duration": data.duration,
        "concentration": data.concentration,
        "ritual": data.ritual,
        "description": data.description,
        "higher_levels": data.higher_levels,
        "available_classes": data.available_classes,
        "available_races": data.available_races,
        "available_subclasses": data.available_subclasses,
        "spellcasting_ability": data.spellcasting_ability,
        "spell_source": data.spell_source,
    }


def spell_to_response(row) -> SpellResponse:
    return SpellResponse(
        id=row.id,
        spell_name=row.spell_name,
        spell_level=row.spell_level,
        school=row.school,
        casting_time=row.casting_time,
        range=row.range,
        components=row.components,
        material_components=row.material_components,
        duration=row.duration,
        concentration=row.concentration,
        ritual=row.ritual,
        description=row.description,
        higher_levels=row.higher_levels,
        available_classes=row.available_classes or [],
        available_races=row.available_races or [],
        available_subclasses=row.available_subclasses or [],
        spellcasting_ability=row.spellcasting_ability,
        spell_source=row.spell_source,
    )


# --- Class feature ---

def feature_to_orm(data: FeatureSchema) -> dict[str, Any]:
    return {
        "feature_name": data.feature_name,
        "feature_source": data.feature_source,
        "class_source": data.class_source,
        "level_required": data.level_required,
        "description": data.description,
        "category": data.category,
        "resource_key": data.resource_key,
        "is_optional": data.is_optional,
        "effects": [effect.model_dump(mode="json") for effect in data.effects],
        "options": _dump_list(data.options),
        "prerequisite_features": data.prerequisite_features,
    }


def feature_to_response(row) -> FeatureResponse:
    return FeatureResponse(
        id=row.id,
        feature_name=row.feature_name,
        feature_source=row.feature_source,
        class_source=row.class_source,
        level_required=row.level_required,
        description=row.description,
        category=row.category,
        resource_key=row.resource_key,
        is_optional=row.is_optional,
        effects=row.effects or [],
        options=row.options,
        prerequisite_features=row.prerequisite_features or [],
    )


# --- Class resource ---

def class_resource_to_orm(data: ClassResourceSchema) -> dict[str, Any]:
    return {
        "resource_key": data.resource_key,
        "resource_name": data.resource_name,
        "class_source": data.class_source,
        "kind": data.kind,
        "description": data.description,
        "recharge": data.recharge,
        "level_scaling": _dump_optional(data.level_scaling),
        "collection_catalog": [entry.model_dump(mode="json") for entry in data.collection_catalog],
        "collection_size_scaling": _dump_optional(data.collection_size_scaling),
        "activation_effects": [effect.model_dump(mode="json") for effect in data.activation_effects],
        "passive_effects": [effect.model_dump(mode="json") for effect in data.passive_effects],
        "level_required": data.level_required,
    }


def class_resource_to_response(row) -> ClassResourceResponse:
    return ClassResourceResponse(
        id=row.id,
        resource_key=row.resource_key,
        resource_name=row.resource_name,
        class_source=row.class_source,
        kind=row.kind,
        description=row.description,
        recharge=row.recharge,
        level_scaling=row.level_scaling,
        collection_catalog=row.collection_catalog or [],
        collection_size_scaling=row.collection_size_scaling,
        activation_effects=row.activation_effects or [],
        passive_effects=row.passive_effects or [],
        level_required=row.level_required,
    )


# --- Creature ---

def creature_to_orm(data: CreatureSchema) -> dict[str, Any]:
    return {
        "is_npc": data.is_npc,
        "community_id": data.community_id,
        "name": data.name,
        "is_unique": data.is_unique,
        "description": data.description,
        "image_url": data.image_url,
        "settings_id": data.settings_id,
        "book_source_id": data.book_source_id,
        "size": data.size,
        "creature_type": data.creature_type,
        "alignment": data.alignment,
        "ac": data.ac,
        "ac_source": data.ac_source,
        "hp": data.hp,
        "hp_formula": data.hp_formula,
        "speed": data.speed,
        "flight_speed": data.flight_speed,
        "swim_speed": data.swim_speed,
        "burrow_speed": data.burrow_speed,
        "climb_speed": data.climb_speed,
        "strenght": data.strenght,
        "dexterity": data.dexterity,
        "constitution": data.constitution,
        "intelligence": data.intelligence,
        "wisdom": data.wisdom,
        "charisma": data.charisma,
        "saving_throws": data.saving_throws,
        "skills": data.skills,
        "damage_imunities": data.damage_imunities,
        "damage_resistances": data.damage_resistances,
        "damage_vulnerabilities": data.damage_vulnerabilities,
        "condition_imunities": data.condition_imunities,
        "night_vision": data.night_vision,
        "blind_vision": data.blind_vision,
        "true_vision": data.true_vision,
        "languages": data.languages,
        "can_speak": data.can_speak,
        "challenge_rating": data.challenge_rating,
        "proficiency_bonus": data.proficiency_bonus,
        "area_of_living": data.area_of_living,
        "features": data.features,
        "actions": data.actions,
        "actions_description": data.actions_description,
        "legendary_actions": data.legendary_actions,
        "legendary_description": data.legendary_description,
        "mythical_actions": data.mythical_actions,
        "mythical_description": data.mythical_description,
        "creature_description": data.creature_description,
        "image_gallery": data.image_gallery,
    }


def creature_to_response(row) -> CreatureResponse:
    return CreatureResponse(
        id=row.id,
        is_npc=row.is_npc,
        community_id=row.community_id,
        name=row.name,
        is_unique=row.is_unique,
        description=row.description,
        image_url=row.image_url,
        settings_id=row.settings_id,
        book_source_id=row.book_source_id,
        size=row.size,
        creature_type=row.creature_type,
        alignment=row.alignment,
        ac=row.ac,
        ac_source=row.ac_source,
        hp=row.hp,
        hp_formula=row.hp_formula,
        speed=row.speed,
        flight_speed=row.flight_speed,
        swim_speed=row.swim_speed,
        burrow_speed=row.burrow_speed,
        climb_speed=row.climb_speed,
        strenght=row.strenght,
        dexterity=row.dexterity,
        constitution=row.constitution,
        intelligence=row.intelligence,
        wisdom=row.wisdom,
        charisma=row.charisma,
        saving_throws=row.saving_throws,
        skills=row.skills,
        damage_imunities=row.damage_imunities,
        damage_resistances=row.damage_resistances,
        damage_vulnerabilities=row.damage_vulnerabilities,
        condition_imunities=row.condition_imunities,
        night_vision=row.night_vision,
        blind_vision=row.blind_vision,
        true_vision=row.true_vision,
        languages=row.languages,
        can_speak=row.can_speak,
        challenge_rating=row.challenge_rating,
        proficiency_bonus=row.proficiency_bonus,
        area_of_living=row.area_of_living,
        features=row.features,
        actions=row.actions,
        actions_description=row.actions_description,
        legendary_actions=row.legendary_actions,
        legendary_description=row.legendary_description,
        mythical_actions=row.mythical_actions,
        mythical_description=row.mythical_description,
        creature_description=row.creature_description,
        image_gallery=row.image_gallery,
    )


# --- Character ---

def character_to_orm(data: CharacterSchema) -> dict[str, Any]:
    return {
        "player_id": data.player_id,
        "character_name": data.character_name,
        "payload": data.model_dump(mode="json"),
    }


def character_to_response(row) -> CharacterResponse:
    payload = row.payload or {}
    return CharacterResponse.model_validate({"id": row.id, **payload})


# --- Campaign ---

def campaign_to_orm(data: Campaign) -> dict[str, Any]:
    content_raw = _dump_list(data.content)
    if content_raw is None and data.chapters:
        content_raw = chapters_to_content(
            [c.model_dump(mode="json") if hasattr(c, "model_dump") else c for c in data.chapters]
        )
    normalized = normalize_campaign_content(content_raw)
    return {
        "name": data.name,
        "description": data.description,
        "image_gallery": data.image_gallery,
        "settings_id": data.settings_id,
        "book_source_id": data.book_source_id,
        "order": data.order,
        "campaign_type": data.campaign_type,
        "campaign_lenght": data.campaign_lenght,
        "campaign_setting": data.campaign_setting,
        "preferable_system": data.preferable_system,
        "preferable_player_count": data.preferable_player_count,
        "preferable_player_minimum_level": data.preferable_player_minimum_level,
        "preferable_player_maximum_level": data.preferable_player_maximum_level,
        "content": normalized,
        "chapters": _dump_list(data.chapters),
        "custom_creatures": data.custom_creatures,
        "custom_locations": data.custom_locations,
        "custom_communities": data.custom_communities,
    }


def campaign_to_response(row) -> CampaignResponse:
    content = row.content
    if not content and row.chapters:
        content = chapters_to_content(row.chapters)
    normalized = normalize_campaign_content(content)
    return CampaignResponse(
        id=row.id,
        name=row.name,
        description=row.description,
        image_gallery=row.image_gallery,
        settings_id=row.settings_id,
        book_source_id=row.book_source_id,
        order=row.order,
        campaign_type=row.campaign_type,
        campaign_lenght=row.campaign_lenght,
        campaign_setting=row.campaign_setting,
        preferable_system=row.preferable_system,
        preferable_player_count=row.preferable_player_count,
        preferable_player_minimum_level=row.preferable_player_minimum_level,
        preferable_player_maximum_level=row.preferable_player_maximum_level,
        content=normalized,
        chapters=row.chapters,
        custom_creatures=row.custom_creatures,
        custom_locations=row.custom_locations,
        custom_communities=row.custom_communities,
    )


# --- Location ---

def location_to_orm(data: LocationSchema) -> dict[str, Any]:
    return {
        "name": data.name,
        "description": data.description,
        "image_gallery": data.image_gallery,
        "settings_id": data.settings_id,
        "book_source_id": data.book_source_id,
        "location_type": data.location_type,
        "super_location": data.super_location,
        "community_id": data.community_id,
    }


def location_to_response(row) -> LocationResponse:
    return LocationResponse(
        id=row.id,
        name=row.name,
        description=row.description,
        image_gallery=row.image_gallery,
        settings_id=row.settings_id,
        book_source_id=row.book_source_id,
        location_type=row.location_type,
        super_location=row.super_location,
        community_id=row.community_id,
    )


# --- Community ---

def community_to_orm(data: CommunitySchema) -> dict[str, Any]:
    return {
        "name": data.name,
        "description": data.description,
        "image_gallery": data.image_gallery,
        "settings_id": data.settings_id,
        "book_source_id": data.book_source_id,
        "community_type": data.community_type,
    }


def community_to_response(row) -> CommunityResponse:
    return CommunityResponse(
        id=row.id,
        name=row.name,
        description=row.description,
        image_gallery=row.image_gallery,
        settings_id=row.settings_id,
        book_source_id=row.book_source_id,
        community_type=row.community_type,
    )


# --- Religion ---

def religion_to_orm(data: ReligionSchema) -> dict[str, Any]:
    return {
        "name": data.name,
        "description": data.description,
        "image_gallery": data.image_gallery,
        "settings_id": data.settings_id,
        "book_source_id": data.book_source_id,
    }


def religion_to_response(row) -> ReligionResponse:
    return ReligionResponse(
        id=row.id,
        name=row.name,
        description=row.description,
        image_gallery=row.image_gallery,
        settings_id=row.settings_id,
        book_source_id=row.book_source_id,
    )


# --- Termins ---

def termins_to_orm(data: TerminsSchema) -> dict[str, Any]:
    return {
        "name": data.name,
        "description": data.description,
        "image_gallery": data.image_gallery,
        "book_source_id": data.book_source_id,
    }


def termins_to_response(row) -> TerminsResponse:
    return TerminsResponse(
        id=row.id,
        name=row.name,
        description=row.description,
        image_gallery=row.image_gallery,
        book_source_id=row.book_source_id,
    )


# --- Item ---

def item_schema_to_orm(item_data: ItemSchema, item_image_id: int | None = None) -> dict[str, Any]:
    return {
        "item_name": item_data.item_name,
        "item_type": item_data.item_type,
        "rarity": item_data.rarity,
        "attunement_required": item_data.attunement_required,
        "weight": item_data.weight,
        "cost_copper": item_data.cost_copper,
        "description": item_data.description,
        "item_source": item_data.item_source,
        "item_image_id": item_image_id,
        "weapon_details": item_data.weapon.model_dump(mode="json") if item_data.weapon else None,
        "armor_details": item_data.armor.model_dump(mode="json") if item_data.armor else None,
        "tool_category": item_data.tool_category,
        "equipped_effects": [effect.model_dump(mode="json") for effect in item_data.equipped_effects],
        "item_image_gallery": item_data.item_image_gallery,
    }

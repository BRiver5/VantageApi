from __future__ import annotations

from typing import Any, Callable


def sort_by_order(items: list[dict[str, Any]] | None, key: str = "order") -> list[dict[str, Any]] | None:
    if not items:
        return items
    return sorted(items, key=lambda x: x.get(key, 0) if isinstance(x, dict) else getattr(x, key, 0))


def reindex_orders(items: list[Any]) -> list[Any]:
    result = []
    for index, item in enumerate(items):
        if isinstance(item, dict):
            result.append({**item, "order": index})
        else:
            data = item.model_dump() if hasattr(item, "model_dump") else dict(item)
            data["order"] = index
            result.append(type(item)(**data) if hasattr(item, "model_dump") else data)
    return result


def normalize_sub_races(sub_races: list[Any] | None) -> list[Any] | None:
    if not sub_races:
        return sub_races
    sorted_sub_races = sort_by_order(sub_races)
    return reindex_orders(sorted_sub_races or [])


def normalize_campaign_content(content: list[Any] | None) -> list[Any] | None:
    if not content:
        return content
    sorted_blocks = sorted(
        content,
        key=lambda b: (b.get("order", 0) if isinstance(b, dict) else getattr(b, "order", 0)),
    )
    normalized = []
    for index, block in enumerate(sorted_blocks):
        if isinstance(block, dict):
            entry = {**block, "order": index}
            dungeon = entry.get("dungeon")
            if dungeon and isinstance(dungeon, dict) and dungeon.get("rooms"):
                rooms = sort_by_order(dungeon["rooms"])
                entry["dungeon"] = {**dungeon, "rooms": reindex_orders(rooms or [])}
        else:
            entry = block.model_dump()
            entry["order"] = index
        normalized.append(entry)
    return normalized


def chapters_to_content(chapters: list[Any] | None) -> list[dict[str, Any]] | None:
    if not chapters:
        return None
    return [
        {"order": index, "kind": "chapter", "chapter": ch, "dungeon": None}
        for index, ch in enumerate(chapters)
    ]

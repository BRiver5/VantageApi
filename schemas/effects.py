from __future__ import annotations

from typing import Callable, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")

# Когда вызывается эффект (аналог «хука» / точки входа функции)
EffectTrigger = Literal[
    "passive",       # пока выполнены conditions (надет, настроен и т.д.)
    "on_equip",
    "on_unequip",
    "on_attune",
    "on_unattune",
    "on_short_rest",
    "on_long_rest",
    "on_combat_start",
    "on_turn_start",
    "on_activate",    # ярость, благоволение и т.п.
    "on_deactivate",
]

# Условие срабатывания; все conditions в одном эффекте — логическое AND
EffectConditionKind = Literal[
    "equipped",
    "attuned",
    "item_slot",      # params: slot
    "min_character_level",
    "has_class",      # params: class_name
    "class_level_min",  # params: class_name, level
]

# Тело эффекта (аналог return / side-effect функции)
EffectActionKind = Literal[
    "modify_stat",
    "set_stat",
    "grant_advantage",
    "grant_disadvantage",
    "add_proficiency",
    "add_language",
    "add_resistance",
    "add_immunity",
]

EffectOperation = Literal["add", "set", "multiply", "max", "min"]


class effect_condition(BaseModel):
    kind: EffectConditionKind
    slot: str | None = None
    class_name: str | None = None
    level: int | None = None
    value: int | str | bool | None = None


class effect_action(BaseModel):
    """Декларативное действие. Интерпретируется движком эффектов на сервере."""
    kind: EffectActionKind
    target: str
    value: int | float | str | bool
    operation: EffectOperation = "add"


class functional_effect(BaseModel):
    """
    Условный эффект: trigger + conditions → action.

    handler_key — опциональный идентификатор кастомной функции в реестре сервера,
    когда декларативного action недостаточно (см. register_effect_handler).
    """
    trigger: EffectTrigger
    conditions: list[effect_condition] = Field(default_factory=list)
    action: effect_action
    handler_key: str | None = None
    notes: str | None = None


# Пример: Кольцо защиты (+1 КД, пока надето и настроено)
# functional_effect(
#     trigger="passive",
#     conditions=[
#         effect_condition(kind="equipped"),
#         effect_condition(kind="attuned"),
#         effect_condition(kind="item_slot", slot="ring"),
#     ],
#     action=effect_action(kind="modify_stat", target="armor_class", value=1),
#     notes="Ring of Protection",
# )

_effect_handlers: dict[str, Callable[..., T]] = {}


def register_effect_handler(
    key: str, handler: Callable[..., T] | None = None
) -> Callable[..., T] | Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Регистрация кастомной функции по handler_key.

    @register_effect_handler("my_effect")
    def my_effect(character, effect): ...
    """
    if handler is not None:
        _effect_handlers[key] = handler
        return handler

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        _effect_handlers[key] = fn
        return fn

    return decorator


def get_effect_handler(key: str) -> Callable[..., T] | None:
    return _effect_handlers.get(key)

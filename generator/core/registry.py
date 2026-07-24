from __future__ import annotations

from generator.core.exceptions import GeneratorNotFoundError, ValidationError


class GeneratorRegistry:
    def __init__(self):
        self._items = {}

    def register(self, name, generator_type):
        key = name.strip().lower()
        if not key:
            raise ValidationError("Generator 名稱不可為空")
        if key in self._items:
            raise ValidationError(f"Generator 已註冊：{key}")
        self._items[key] = generator_type

    def create(self, name):
        key = name.strip().lower()
        if key not in self._items:
            raise GeneratorNotFoundError(f"找不到 Generator：{name}")
        return self._items[key]()

    def names(self):
        return tuple(sorted(self._items))

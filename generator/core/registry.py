from __future__ import annotations

from generator.core.exceptions import GeneratorNotFoundError, ValidationError


class GeneratorRegistry:
    """管理可用 Generator 類型的註冊與建立。"""

    def __init__(self):
        self._items = {}

    def register(self, name, generator_type):
        """以名稱註冊 Generator 類型。"""
        key = name.strip().lower()
        if not key:
            raise ValidationError("Generator 名稱不可為空")
        if key in self._items:
            raise ValidationError(f"Generator 已註冊：{key}")
        self._items[key] = generator_type

    def create(self, name):
        """依名稱建立 Generator instance。"""
        key = name.strip().lower()
        if key not in self._items:
            raise GeneratorNotFoundError(f"找不到 Generator：{name}")
        return self._items[key]()

    def names(self):
        """回傳已註冊的 Generator 名稱。"""
        return tuple(sorted(self._items))

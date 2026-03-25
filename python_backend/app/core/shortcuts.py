from collections import defaultdict
from typing import Dict, Optional

from app.features.redis_cache import cache


class ShortcutManager:
    """
    Per-user shortcut (abbreviation) manager.
    Example: 'slm' -> 'selam'
    """

    def __init__(self) -> None:
        self.PREFIX = "shortcuts"
        self.local_shortcuts: Dict[str, Dict[str, str]] = defaultdict(dict)

    def _key(self, user_id: str) -> str:
        return f"{self.PREFIX}:{user_id}"

    def add_shortcut(self, user_id: str, short: str, full: str) -> None:
        short = (short or "").strip().lower()
        full = (full or "").strip()
        if not short or not full or len(short) > len(full):
            return

        if cache and cache.available:
            try:
                cache.client.hset(self._key(user_id), short, full)
                return
            except Exception:
                pass

        self.local_shortcuts[user_id][short] = full

    def get_shortcut(self, user_id: str, short: str) -> Optional[str]:
        short = (short or "").strip().lower()
        if not short:
            return None

        if cache and cache.available:
            try:
                val = cache.client.hget(self._key(user_id), short)
                if val:
                    return val
            except Exception:
                pass

        return self.local_shortcuts.get(user_id, {}).get(short)

    def get_all_for_user(self, user_id: str) -> Dict[str, str]:
        if cache and cache.available:
            try:
                raw = cache.client.hgetall(self._key(user_id))
                return {k: v for k, v in raw.items()}
            except Exception:
                pass
        return dict(self.local_shortcuts.get(user_id, {}))


shortcuts_manager = ShortcutManager()


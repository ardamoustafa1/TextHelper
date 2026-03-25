from collections import defaultdict
from typing import Dict

from app.features.redis_cache import cache


class AutoCorrectManager:
    """
    Tracks per-user auto-correct blacklists.
    If a user undoes a correction for a word, we stop auto-applying it.
    """

    def __init__(self) -> None:
        self.PREFIX = "ac:blacklist"
        self.local_blacklist: Dict[str, Dict[str, bool]] = defaultdict(dict)

    def _key(self, user_id: str) -> str:
        return f"{self.PREFIX}:{user_id}"

    def block(self, user_id: str, original: str) -> None:
        original = (original or "").strip().lower()
        if not original:
            return

        if cache and cache.available:
            try:
                cache.client.hset(self._key(user_id), original, 1)
                return
            except Exception:
                pass

        self.local_blacklist[user_id][original] = True

    def is_blocked(self, user_id: str, original: str) -> bool:
        original = (original or "").strip().lower()
        if not original:
            return False

        if cache and cache.available:
            try:
                val = cache.client.hget(self._key(user_id), original)
                if val:
                    return True
            except Exception:
                pass

        return self.local_blacklist.get(user_id, {}).get(original, False)


autocorrect_manager = AutoCorrectManager()


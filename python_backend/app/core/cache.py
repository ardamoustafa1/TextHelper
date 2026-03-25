import json
import logging
from typing import Optional, Any

import redis

from app.core.config import settings

logger = logging.getLogger("TextHelperCache")


class CacheManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return

        self.use_redis = False
        self.redis_client = None
        self.memory_cache = {}
        self.max_memory_size = 1000

        # Try connecting to Redis using configured host/port
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0,
                socket_connect_timeout=1,
            )
            self.redis_client.ping()
            self.use_redis = True
            logger.info("[CACHE] Redis connected successfully.")
        except redis.ConnectionError:
            logger.info(
                "[CACHE] Redis not available. High-performance in-memory cache is active."
            )
            self.use_redis = False
        except Exception as e:
            logger.info(
                f"[CACHE] Falling back to in-memory cache due to error: {e}"
            )
            self.use_redis = False

        self.initialized = True

    def get(self, key: str) -> Optional[Any]:
        if self.use_redis:
            try:
                val = self.redis_client.get(key)
                if val:
                    return json.loads(val)
            except Exception:
                return None
        else:
            return self.memory_cache.get(key)

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        if self.use_redis:
            try:
                self.redis_client.setex(key, ttl, json.dumps(value))
            except Exception:
                # Fail silently; caller should still work without cache
                return
        else:
            # Automatic cleanup if too big
            if len(self.memory_cache) > self.max_memory_size:
                self.memory_cache.pop(next(iter(self.memory_cache)))
            self.memory_cache[key] = value


cache_manager = CacheManager()

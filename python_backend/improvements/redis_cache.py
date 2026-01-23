"""
Redis Cache Layer - Performans İyileştirmesi
"""

import redis
import json
from typing import Optional, Any
from datetime import timedelta
import hashlib

class RedisCache:
    """Redis cache katmanı"""
    
    def __init__(self, host='localhost', port=6379, db=0):
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=2
            )
            # Bağlantı testi
            self.client.ping()
            self.available = True
            print("[OK] Redis cache baglantisi kuruldu")
        except Exception as e:
            print(f"[WARNING] Redis kullanilamiyor, memory cache kullanilacak: {e}")
            self.client = None
            self.available = False
            self.memory_cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Cache'den al"""
        if not self.available:
            return self.memory_cache.get(key)
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            print(f"Cache get hatası: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Cache'e kaydet"""
        if not self.available:
            self.memory_cache[key] = value
            return
        
        try:
            self.client.setex(
                key,
                ttl,
                json.dumps(value, ensure_ascii=False)
            )
        except Exception as e:
            print(f"Cache set hatası: {e}")
    
    def delete(self, key: str):
        """Cache'den sil"""
        if not self.available:
            self.memory_cache.pop(key, None)
            return
        
        try:
            self.client.delete(key)
        except Exception as e:
            print(f"Cache delete hatası: {e}")
    
    def clear_pattern(self, pattern: str):
        """Pattern'e uyan tüm key'leri sil"""
        if not self.available:
            keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
            for k in keys_to_delete:
                del self.memory_cache[k]
            return
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
        except Exception as e:
            print(f"Cache clear hatası: {e}")
    
    def generate_key(self, *args) -> str:
        """Cache key oluştur"""
        key_string = ":".join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()

# Global instance
cache = RedisCache()

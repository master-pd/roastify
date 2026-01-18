"""
Advanced Redis Cache Manager with Multiple Strategies
"""

import redis.asyncio as redis
import json
import pickle
from typing import Any, Optional, Union, Dict, List
from datetime import timedelta
import hashlib
from functools import wraps
import asyncio

class CacheManager:
    """Advanced cache manager with Redis backend"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.client: Optional[redis.Redis] = None
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
        
    async def connect(self):
        """Connect to Redis"""
        self.client = await redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=False,
            max_connections=50,
            socket_keepalive=True
        )
        
    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            
    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key"""
        key_parts = [prefix]
        
        # Add args
        for arg in args:
            key_parts.append(str(arg))
            
        # Add kwargs
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
            
        # Create hash
        key_string = ":".join(key_parts)
        return f"roastify:{hashlib.md5(key_string.encode()).hexdigest()}"
        
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        if not self.client:
            return default
            
        try:
            value = await self.client.get(key)
            if value:
                self.stats['hits'] += 1
                return pickle.loads(value)
            else:
                self.stats['misses'] += 1
                return default
        except Exception as e:
            # Log error but don't crash
            return default
            
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache"""
        if not self.client:
            return
            
        try:
            serialized = pickle.dumps(value)
            await self.client.setex(key, ttl, serialized)
            self.stats['sets'] += 1
        except Exception as e:
            # Log error
            pass
            
    async def delete(self, key: str):
        """Delete value from cache"""
        if not self.client:
            return
            
        try:
            await self.client.delete(key)
            self.stats['deletes'] += 1
        except Exception:
            pass
            
    async def get_or_set(self, key: str, callback, ttl: int = 3600) -> Any:
        """Get from cache or set if not exists"""
        cached = await self.get(key)
        if cached is not None:
            return cached
            
        # Not in cache, call callback
        value = await callback() if asyncio.iscoroutinefunction(callback) else callback()
        await self.set(key, value, ttl)
        return value
        
    async def invalidate_pattern(self, pattern: str):
        """Invalidate cache by pattern"""
        if not self.client:
            return
            
        try:
            keys = await self.client.keys(pattern)
            if keys:
                await self.client.delete(*keys)
        except Exception:
            pass
            
    # Specialized cache methods
    async def cache_user_data(self, user_id: int, data: Dict):
        """Cache user data"""
        key = self.generate_key("user", user_id)
        await self.set(key, data, ttl=1800)  # 30 minutes
        
    async def get_user_data(self, user_id: int) -> Optional[Dict]:
        """Get cached user data"""
        key = self.generate_key("user", user_id)
        return await self.get(key)
        
    async def cache_roast(self, text: str, roast_data: Dict):
        """Cache roast result"""
        key = self.generate_key("roast", text[:100])
        await self.set(key, roast_data, ttl=1800)  # 30 minutes
        
    async def get_cached_roast(self, text: str) -> Optional[Dict]:
        """Get cached roast"""
        key = self.generate_key("roast", text[:100])
        return await self.get(key)
        
    async def cache_image(self, image_key: str, image_path: str):
        """Cache image reference"""
        key = self.generate_key("image", image_key)
        await self.set(key, image_path, ttl=86400)  # 24 hours
        
    async def get_cached_image(self, image_key: str) -> Optional[str]:
        """Get cached image path"""
        key = self.generate_key("image", image_key)
        return await self.get(key)
        
    async def cache_group_settings(self, chat_id: int, settings: Dict):
        """Cache group settings"""
        key = self.generate_key("group", chat_id)
        await self.set(key, settings, ttl=3600)  # 1 hour
        
    async def get_group_settings(self, chat_id: int) -> Optional[Dict]:
        """Get cached group settings"""
        key = self.generate_key("group", chat_id)
        return await self.get(key)
        
    async def increment_counter(self, counter_name: str, amount: int = 1) -> int:
        """Increment counter atomically"""
        if not self.client:
            return 0
            
        key = f"counter:{counter_name}"
        return await self.client.incrby(key, amount)
        
    async def get_counter(self, counter_name: str) -> int:
        """Get counter value"""
        if not self.client:
            return 0
            
        key = f"counter:{counter_name}"
        value = await self.client.get(key)
        return int(value) if value else 0
        
    async def add_to_list(self, list_name: str, value: str):
        """Add to Redis list"""
        if not self.client:
            return
            
        key = f"list:{list_name}"
        await self.client.lpush(key, value)
        await self.client.ltrim(key, 0, 999)  # Keep last 1000 items
        
    async def get_list(self, list_name: str, limit: int = 100) -> List[str]:
        """Get Redis list"""
        if not self.client:
            return []
            
        key = f"list:{list_name}"
        return await self.client.lrange(key, 0, limit - 1)
        
    async def add_to_set(self, set_name: str, value: str):
        """Add to Redis set"""
        if not self.client:
            return
            
        key = f"set:{set_name}"
        await self.client.sadd(key, value)
        
    async def is_in_set(self, set_name: str, value: str) -> bool:
        """Check if value in set"""
        if not self.client:
            return False
            
        key = f"set:{set_name}"
        return await self.client.sismember(key, value) == 1
        
    async def publish_event(self, channel: str, data: Dict):
        """Publish event to Redis pub/sub"""
        if not self.client:
            return
            
        await self.client.publish(channel, json.dumps(data))
        
    async def subscribe(self, channel: str, callback):
        """Subscribe to Redis channel"""
        if not self.client:
            return
            
        pubsub = self.client.pubsub()
        await pubsub.subscribe(channel)
        
        async for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                await callback(data)
                
    async def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            **self.stats,
            'hit_rate': self.stats['hits'] / max(1, self.stats['hits'] + self.stats['misses']),
            'size': await self.get_memory_usage() if self.client else 0
        }
        
    async def get_memory_usage(self) -> int:
        """Get Redis memory usage"""
        if not self.client:
            return 0
            
        info = await self.client.info('memory')
        return info.get('used_memory', 0)
        
    async def clear_all(self):
        """Clear all cache (use with caution!)"""
        if not self.client:
            return
            
        await self.client.flushdb()
        
    # Decorator for caching function results
    def cached(self, ttl: int = 3600, key_prefix: str = "func"):
        """Decorator to cache function results"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self.generate_key(
                    key_prefix,
                    func.__name__,
                    *args,
                    **{k: v for k, v in kwargs.items() if k not in ['self', 'cls']}
                )
                
                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                    
                # Execute function
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                
                # Cache result
                await self.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
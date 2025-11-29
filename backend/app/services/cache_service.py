"""Redis cache service for caching AI responses."""

import json
import hashlib
from typing import Optional, Any
import redis
from redis.exceptions import ConnectionError, TimeoutError

from ..config import get_settings


class CacheService:
    """Service for caching AI responses using Redis."""
    
    def __init__(self):
        settings = get_settings()
        self._enabled = settings.redis_enabled
        self._ttl_analysis = settings.redis_ttl_analysis  # TTL for analysis results (hours)
        self._ttl_generation = settings.redis_ttl_generation  # TTL for generation results (hours)
        
        if not self._enabled:
            self._redis_client = None
            return
        
        try:
            self._redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                socket_connect_timeout=2,
                socket_timeout=2,
                decode_responses=True
            )
            # Test connection
            self._redis_client.ping()
            print("[CACHE] Redis connection established")
        except (ConnectionError, TimeoutError, Exception) as e:
            print(f"[CACHE] Redis connection failed: {e}. Cache disabled.")
            self._redis_client = None
            self._enabled = False
    
    def _generate_key(self, prefix: str, *args: Any) -> str:
        """Generate cache key from arguments."""
        key_data = json.dumps(args, sort_keys=True, ensure_ascii=False)
        key_hash = hashlib.sha256(key_data.encode('utf-8')).hexdigest()
        return f"bizmail:{prefix}:{key_hash}"
    
    def get(self, prefix: str, *args: Any) -> Optional[Any]:
        """Get cached value."""
        if not self._enabled or not self._redis_client:
            return None
        
        try:
            key = self._generate_key(prefix, *args)
            cached = self._redis_client.get(key)
            if cached:
                print(f"[CACHE] HIT: {prefix}")
                return json.loads(cached)
            print(f"[CACHE] MISS: {prefix}")
            return None
        except Exception as e:
            print(f"[CACHE] Error getting cache: {e}")
            return None
    
    def set(self, prefix: str, value: Any, ttl_hours: int, *args: Any) -> bool:
        """Set cached value."""
        if not self._enabled or not self._redis_client:
            return False
        
        try:
            key = self._generate_key(prefix, *args)
            ttl_seconds = ttl_hours * 3600
            serialized = json.dumps(value, ensure_ascii=False)
            self._redis_client.setex(key, ttl_seconds, serialized)
            print(f"[CACHE] SET: {prefix} (TTL: {ttl_hours}h)")
            return True
        except Exception as e:
            print(f"[CACHE] Error setting cache: {e}")
            return False
    
    def get_analysis(self, subject: str, body: str, company_context: str) -> Optional[dict]:
        """Get cached analysis result."""
        return self.get("analysis", subject, body, company_context)
    
    def set_analysis(self, subject: str, body: str, company_context: str, result: dict) -> bool:
        """Cache analysis result."""
        return self.set("analysis", result, self._ttl_analysis, subject, body, company_context)
    
    def get_generation(
        self,
        source_subject: str,
        source_body: str,
        company_context: str,
        parameters_hash: str,
        thread_history: Optional[str] = None,
        extra_directives: Optional[list] = None,
        custom_prompt: Optional[str] = None
    ) -> Optional[dict]:
        """Get cached generation result."""
        return self.get(
            "generation",
            source_subject,
            source_body,
            company_context,
            parameters_hash,
            thread_history or "",
            json.dumps(extra_directives or [], sort_keys=True),
            custom_prompt or ""
        )
    
    def set_generation(
        self,
        source_subject: str,
        source_body: str,
        company_context: str,
        parameters_hash: str,
        result: dict,
        thread_history: Optional[str] = None,
        extra_directives: Optional[list] = None,
        custom_prompt: Optional[str] = None
    ) -> bool:
        """Cache generation result."""
        return self.set(
            "generation",
            result,
            self._ttl_generation,
            source_subject,
            source_body,
            company_context,
            parameters_hash,
            thread_history or "",
            json.dumps(extra_directives or [], sort_keys=True),
            custom_prompt or ""
        )
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern."""
        if not self._enabled or not self._redis_client:
            return 0
        
        try:
            keys = self._redis_client.keys(f"bizmail:{pattern}*")
            if keys:
                return self._redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"[CACHE] Error clearing cache: {e}")
            return 0
    
    def is_enabled(self) -> bool:
        """Check if cache is enabled."""
        return self._enabled


# Singleton instance
_cache_service = None

def get_cache_service() -> CacheService:
    """Get singleton cache service instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


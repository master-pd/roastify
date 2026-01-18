"""
Advanced Rate Limiter with Multiple Strategies
"""

import time
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import asyncio
from dataclasses import dataclass
from enum import Enum

class RateLimitStrategy(Enum):
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"

@dataclass
class RateLimitRule:
    """Rate limiting rule configuration"""
    strategy: RateLimitStrategy
    requests_per_period: int
    period_seconds: int
    burst_limit: Optional[int] = None
    cost_per_request: int = 1
    
class RateLimiter:
    """Advanced rate limiter with multiple strategies"""
    
    def __init__(self):
        self.rules: Dict[str, RateLimitRule] = {}
        self.counters: Dict[str, Dict] = defaultdict(dict)
        self.locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        
    def add_rule(self, key: str, rule: RateLimitRule):
        """Add rate limiting rule"""
        self.rules[key] = rule
        
    def add_default_rules(self):
        """Add default rate limiting rules"""
        # User-level limits
        self.add_rule("user:message", RateLimitRule(
            strategy=RateLimitStrategy.SLIDING_WINDOW,
            requests_per_period=30,
            period_seconds=60,
            burst_limit=50
        ))
        
        self.add_rule("user:command", RateLimitRule(
            strategy=RateLimitStrategy.TOKEN_BUCKET,
            requests_per_period=10,
            period_seconds=60,
            burst_limit=20
        ))
        
        # Group-level limits
        self.add_rule("group:message", RateLimitRule(
            strategy=RateLimitStrategy.FIXED_WINDOW,
            requests_per_period=100,
            period_seconds=60
        ))
        
        # API limits
        self.add_rule("api:requests", RateLimitRule(
            strategy=RateLimitStrategy.LEAKY_BUCKET,
            requests_per_period=1000,
            period_seconds=3600,
            burst_limit=2000
        ))
        
        # Image generation limits
        self.add_rule("user:image", RateLimitRule(
            strategy=RateLimitStrategy.SLIDING_WINDOW,
            requests_per_period=20,
            period_seconds=3600
        ))
        
    async def check_limit(self, key: str, identifier: str, cost: int = 1) -> Tuple[bool, Dict]:
        """
        Check if request is allowed
        
        Returns: (allowed, info_dict)
        """
        if key not in self.rules:
            return True, {"allowed": True, "reason": "no_rule"}
            
        rule = self.rules[key]
        lock_key = f"{key}:{identifier}"
        
        async with self.locks[lock_key]:
            if rule.strategy == RateLimitStrategy.FIXED_WINDOW:
                return await self._check_fixed_window(key, identifier, rule, cost)
            elif rule.strategy == RateLimitStrategy.SLIDING_WINDOW:
                return await self._check_sliding_window(key, identifier, rule, cost)
            elif rule.strategy == RateLimitStrategy.TOKEN_BUCKET:
                return await self._check_token_bucket(key, identifier, rule, cost)
            elif rule.strategy == RateLimitStrategy.LEAKY_BUCKET:
                return await self._check_leaky_bucket(key, identifier, rule, cost)
                
    async def _check_fixed_window(self, key: str, identifier: str, rule: RateLimitRule, cost: int) -> Tuple[bool, Dict]:
        """Fixed window rate limiting"""
        counter_key = f"{key}:{identifier}"
        window_key = f"{counter_key}:window"
        
        now = int(time.time())
        window_start = now - (now % rule.period_seconds)
        
        if counter_key not in self.counters or self.counters[counter_key].get('window') != window_start:
            # New window
            self.counters[counter_key] = {
                'count': 0,
                'window': window_start,
                'reset_time': window_start + rule.period_seconds
            }
            
        counter = self.counters[counter_key]
        
        # Check burst limit
        if rule.burst_limit and counter['count'] >= rule.burst_limit:
            return False, {
                'allowed': False,
                'reason': 'burst_limit_exceeded',
                'reset_in': counter['reset_time'] - now,
                'current': counter['count'],
                'limit': rule.burst_limit
            }
            
        # Check regular limit
        new_count = counter['count'] + cost
        if new_count > rule.requests_per_period:
            return False, {
                'allowed': False,
                'reason': 'rate_limit_exceeded',
                'reset_in': counter['reset_time'] - now,
                'current': counter['count'],
                'limit': rule.requests_per_period
            }
            
        # Update counter
        counter['count'] = new_count
        
        return True, {
            'allowed': True,
            'remaining': rule.requests_per_period - new_count,
            'reset_in': counter['reset_time'] - now
        }
        
    async def _check_sliding_window(self, key: str, identifier: str, rule: RateLimitRule, cost: int) -> Tuple[bool, Dict]:
        """Sliding window rate limiting"""
        counter_key = f"{key}:{identifier}"
        now = time.time()
        window_start = now - rule.period_seconds
        
        if counter_key not in self.counters:
            self.counters[counter_key] = {
                'timestamps': [],
                'count': 0
            }
            
        counter = self.counters[counter_key]
        
        # Remove old timestamps
        counter['timestamps'] = [ts for ts in counter['timestamps'] if ts > window_start]
        counter['count'] = len(counter['timestamps'])
        
        # Check limit
        if counter['count'] + cost > rule.requests_per_period:
            oldest_request = min(counter['timestamps']) if counter['timestamps'] else now
            reset_in = oldest_request + rule.period_seconds - now
            
            return False, {
                'allowed': False,
                'reason': 'rate_limit_exceeded',
                'reset_in': max(0, reset_in),
                'current': counter['count'],
                'limit': rule.requests_per_period
            }
            
        # Add new request(s)
        for _ in range(cost):
            counter['timestamps'].append(now)
        counter['count'] += cost
        
        # Calculate remaining
        if counter['timestamps']:
            next_reset = min(counter['timestamps']) + rule.period_seconds
            remaining = rule.requests_per_period - counter['count']
        else:
            next_reset = now + rule.period_seconds
            remaining = rule.requests_per_period
            
        return True, {
            'allowed': True,
            'remaining': remaining,
            'reset_in': next_reset - now
        }
        
    async def _check_token_bucket(self, key: str, identifier: str, rule: RateLimitRule, cost: int) -> Tuple[bool, Dict]:
        """Token bucket rate limiting"""
        counter_key = f"{key}:{identifier}"
        now = time.time()
        
        if counter_key not in self.counters:
            self.counters[counter_key] = {
                'tokens': rule.burst_limit or rule.requests_per_period,
                'last_update': now
            }
            
        counter = self.counters[counter_key]
        
        # Add new tokens
        time_passed = now - counter['last_update']
        tokens_to_add = time_passed * (rule.requests_per_period / rule.period_seconds)
        counter['tokens'] = min(
            rule.burst_limit or rule.requests_per_period,
            counter['tokens'] + tokens_to_add
        )
        counter['last_update'] = now
        
        # Check if enough tokens
        if cost > counter['tokens']:
            # Calculate when enough tokens will be available
            tokens_needed = cost - counter['tokens']
            time_needed = tokens_needed / (rule.requests_per_period / rule.period_seconds)
            
            return False, {
                'allowed': False,
                'reason': 'insufficient_tokens',
                'wait_time': time_needed,
                'current_tokens': counter['tokens'],
                'tokens_needed': cost
            }
            
        # Consume tokens
        counter['tokens'] -= cost
        
        # Calculate refill rate
        refill_rate = rule.requests_per_period / rule.period_seconds
        time_to_full = (rule.burst_limit or rule.requests_per_period - counter['tokens']) / refill_rate
        
        return True, {
            'allowed': True,
            'tokens_remaining': counter['tokens'],
            'refill_rate': refill_rate,
            'time_to_full': time_to_full
        }
        
    async def _check_leaky_bucket(self, key: str, identifier: str, rule: RateLimitRule, cost: int) -> Tuple[bool, Dict]:
        """Leaky bucket rate limiting"""
        counter_key = f"{key}:{identifier}"
        now = time.time()
        
        if counter_key not in self.counters:
            self.counters[counter_key] = {
                'water_level': 0,
                'last_leak': now,
                'capacity': rule.burst_limit or rule.requests_per_period
            }
            
        counter = self.counters[counter_key]
        
        # Leak water (process requests)
        time_passed = now - counter['last_leak']
        leak_amount = time_passed * (rule.requests_per_period / rule.period_seconds)
        counter['water_level'] = max(0, counter['water_level'] - leak_amount)
        counter['last_leak'] = now
        
        # Check if bucket has capacity
        if counter['water_level'] + cost > counter['capacity']:
            # Calculate when capacity will be available
            overflow = (counter['water_level'] + cost) - counter['capacity']
            time_needed = overflow / (rule.requests_per_period / rule.period_seconds)
            
            return False, {
                'allowed': False,
                'reason': 'bucket_overflow',
                'wait_time': time_needed,
                'current_level': counter['water_level'],
                'capacity': counter['capacity']
            }
            
        # Add water (add request)
        counter['water_level'] += cost
        
        # Calculate drain time
        drain_time = counter['water_level'] / (rule.requests_per_period / rule.period_seconds)
        
        return True, {
            'allowed': True,
            'water_level': counter['water_level'],
            'drain_time': drain_time,
            'capacity_remaining': counter['capacity'] - counter['water_level']
        }
        
    async def get_usage(self, key: str, identifier: str) -> Optional[Dict]:
        """Get current usage information"""
        counter_key = f"{key}:{identifier}"
        if counter_key not in self.counters:
            return None
            
        rule = self.rules.get(key)
        if not rule:
            return None
            
        counter = self.counters[counter_key]
        
        info = {
            'key': key,
            'identifier': identifier,
            'strategy': rule.strategy.value,
            'limit': rule.requests_per_period,
            'period': rule.period_seconds,
        }
        
        if rule.strategy == RateLimitStrategy.FIXED_WINDOW:
            info.update({
                'current_count': counter.get('count', 0),
                'window_reset': counter.get('reset_time', 0) - time.time()
            })
        elif rule.strategy == RateLimitStrategy.SLIDING_WINDOW:
            info.update({
                'current_count': counter.get('count', 0),
                'request_timestamps': counter.get('timestamps', [])
            })
        elif rule.strategy == RateLimitStrategy.TOKEN_BUCKET:
            info.update({
                'tokens': counter.get('tokens', 0),
                'burst_limit': rule.burst_limit
            })
        elif rule.strategy == RateLimitStrategy.LEAKY_BUCKET:
            info.update({
                'water_level': counter.get('water_level', 0),
                'capacity': counter.get('capacity', 0)
            })
            
        return info
        
    async def reset_limit(self, key: str, identifier: str):
        """Reset rate limit for identifier"""
        counter_key = f"{key}:{identifier}"
        if counter_key in self.counters:
            del self.counters[counter_key]
            
    async def cleanup_old_entries(self, max_age_seconds: int = 86400):
        """Clean up old rate limit entries"""
        now = time.time()
        keys_to_delete = []
        
        for key, counter in self.counters.items():
            if 'last_update' in counter:
                if now - counter['last_update'] > max_age_seconds:
                    keys_to_delete.append(key)
            elif 'last_leak' in counter:
                if now - counter['last_leak'] > max_age_seconds:
                    keys_to_delete.append(key)
                    
        for key in keys_to_delete:
            del self.counters[key]
            
    async def get_global_stats(self) -> Dict:
        """Get global rate limiting statistics"""
        total_requests = 0
        active_limits = 0
        blocked_requests = 0
        
        for counter in self.counters.values():
            if 'count' in counter:
                total_requests += counter['count']
                active_limits += 1
                
        return {
            'total_requests_tracked': total_requests,
            'active_rate_limits': active_limits,
            'total_rules': len(self.rules),
            'memory_usage': len(str(self.counters))  # Approximate
        }
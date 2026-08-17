"""Simple cache-based rate limiting for AI endpoints."""

from django.core.cache import cache
from django.conf import settings


def _limit_settings():
    limit = int(getattr(settings, 'AI_ASSISTANCE_RATE_LIMIT', 20))
    window = int(getattr(settings, 'AI_ASSISTANCE_RATE_WINDOW_SECONDS', 60))
    return limit, window


def client_rate_limit_key(request) -> str:
    if getattr(request, 'user', None) and request.user.is_authenticated:
        return f'ai_rl:user:{request.user.pk}'
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        ip = forwarded.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return f'ai_rl:ip:{ip}'


def is_rate_limited(request) -> bool:
    """Return True if the caller has exceeded the configured rate limit."""
    limit, window = _limit_settings()
    if limit <= 0:
        return False
    key = client_rate_limit_key(request)
    count = cache.get(key, 0)
    if count >= limit:
        return True
    if count == 0:
        cache.set(key, 1, window)
    else:
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, window)
    return False

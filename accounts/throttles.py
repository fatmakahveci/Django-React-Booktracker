import math
import uuid

from django.conf import settings
from django.utils.crypto import salted_hmac
from redis import Redis, RedisError
from rest_framework.exceptions import APIException
from rest_framework.throttling import SimpleRateThrottle

# One Redis operation prunes, counts, and admits a request across all workers.
SLIDING_WINDOW = """
local t = redis.call('TIME')
local now = t[1] * 1000 + math.floor(t[2] / 1000)
redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', now - ARGV[1])
if redis.call('ZCARD', KEYS[1]) >= tonumber(ARGV[2]) then
  local oldest = redis.call('ZRANGE', KEYS[1], 0, 0, 'WITHSCORES')
  return {0, tonumber(oldest[2]) + tonumber(ARGV[1]) - now}
end
redis.call('ZADD', KEYS[1], now, ARGV[3])
redis.call('PEXPIRE', KEYS[1], ARGV[1])
return {1, 0}
"""


class ThrottleUnavailable(APIException):
    status_code = 503
    default_detail = "Authentication is temporarily unavailable. Please retry shortly."


class ClientIPThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, view):
        identity = salted_hmac("auth-rate-limit", self.get_ident(request)).hexdigest()
        return self.cache_format % {"scope": self.scope, "ident": identity}

    def allow_request(self, request, view):
        if not getattr(settings, "AUTH_REDIS_URL", ""):
            return super().allow_request(request, view)
        try:
            with Redis.from_url(
                settings.AUTH_REDIS_URL, socket_timeout=2, socket_connect_timeout=2
            ) as redis:
                admitted, wait_ms = redis.eval(
                    SLIDING_WINDOW,
                    1,
                    self.get_cache_key(request, view),
                    self.duration * 1000,
                    self.num_requests,
                    uuid.uuid4().hex,
                )
        except RedisError as exc:
            raise ThrottleUnavailable() from exc
        self.retry_after = math.ceil(wait_ms / 1000)
        return bool(admitted)

    def wait(self):
        if hasattr(self, "retry_after"):
            return self.retry_after
        return super().wait()


class LoginThrottle(ClientIPThrottle):
    scope = "login"


class RefreshThrottle(ClientIPThrottle):
    scope = "refresh"


class RegistrationThrottle(ClientIPThrottle):
    scope = "registration"


class EmailThrottle(ClientIPThrottle):
    scope = "email"


class AccountThrottle(ClientIPThrottle):
    scope = "account"

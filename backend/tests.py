import json
import os
from concurrent.futures import ThreadPoolExecutor
from unittest import skipUnless
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIRequestFactory

from accounts.throttles import LoginThrottle, ThrottleUnavailable
from backend.observability import scrub_event


class HealthAndLoggingTests(TestCase):
    def test_dependency_failure_is_not_ready_but_process_is_live(self):
        self.assertEqual(self.client.get("/health/ready/").status_code, 200)
        with patch(
            "backend.health.cache.get", side_effect=ConnectionError("secret internal address")
        ):
            result = self.client.get("/health/ready/")
            self.assertEqual(result.status_code, 503)
            self.assertNotIn("secret", result.content.decode())
            self.assertEqual(self.client.get("/health/live/").status_code, 200)

    def test_logs_exclude_query_tokens_and_have_request_id(self):
        with self.assertLogs("booktracker.requests", level="INFO") as logs:
            response = self.client.get("/health/live/?token=secret-token")
        self.assertEqual(len(response["X-Request-ID"]), 32)
        meta = logs.records[0].request_meta
        self.assertNotIn("secret-token", json.dumps(meta))
        self.assertEqual(meta["route"], "health/live/")
        self.assertIn("duration_ms", meta)

    def test_error_report_scrubbing(self):
        result = scrub_event(
            {
                "request": {
                    "method": "POST",
                    "data": {"password": "secret"},
                    "url": "https://example.com/?token=secret",
                    "cookies": "secret",
                },
                "user": {"email": "private"},
                "breadcrumbs": [],
                "exception": {
                    "values": [{"stacktrace": {"frames": [{"vars": {"password": "secret"}}]}}]
                },
            },
            None,
        )
        self.assertNotIn("secret", json.dumps(result))
        self.assertNotIn("user", result)


@skipUnless(os.environ.get("REDIS_URL"), "Requires an isolated REDIS_URL")
class AtomicRedisThrottleTests(SimpleTestCase):
    def test_concurrent_workers_admit_exactly_the_limit(self):
        from redis import Redis

        url = os.environ["REDIS_URL"]
        request = APIRequestFactory().post("/token/", {}, REMOTE_ADDR="192.0.2.199")
        key = LoginThrottle().get_cache_key(request, None)
        with Redis.from_url(url) as redis:
            redis.delete(key)
            try:
                with (
                    override_settings(AUTH_REDIS_URL=url),
                    patch.object(LoginThrottle, "rate", "5/min", create=True),
                ):
                    with ThreadPoolExecutor(max_workers=10) as pool:
                        admitted = list(
                            pool.map(
                                lambda _: LoginThrottle().allow_request(request, None), range(20)
                            )
                        )
                    self.assertEqual(sum(admitted), 5)
                    denied = LoginThrottle()
                    self.assertFalse(denied.allow_request(request, None))
                    self.assertGreater(denied.wait(), 0)
            finally:
                redis.delete(key)

    def test_redis_failure_fails_closed(self):
        request = APIRequestFactory().post("/token/")
        from redis import RedisError

        with (
            override_settings(AUTH_REDIS_URL=os.environ["REDIS_URL"]),
            patch("accounts.throttles.Redis.from_url", side_effect=RedisError),
        ):
            with self.assertRaises(ThrottleUnavailable):
                LoginThrottle().allow_request(request, None)

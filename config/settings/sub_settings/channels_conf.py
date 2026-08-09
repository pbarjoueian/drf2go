"""
Django Channels configuration.

The Redis channel layer is the only layer that works across processes, so it is
the default. ``CHANNEL_LAYER_IN_MEMORY=True`` swaps in the in-memory layer for
tests and for running a single process without Redis - it must never be used
with more than one worker.
"""

from ..env import env
from .redis_conf import REDIS_CONFIG

if env.bool("CHANNEL_LAYER_IN_MEMORY", default=False):
    CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
    }
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                **REDIS_CONFIG,
                "capacity": env.int("CHANNEL_LAYER_CAPACITY", default=1500),
                "expiry": env.int("CHANNEL_LAYER_EXPIRY", default=60),
            },
        },
    }

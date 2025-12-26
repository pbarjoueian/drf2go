"""
Channels configuration settings.

This module contains Channels-related settings for WebSocket support.
"""

# Import Redis configuration
from .redis_conf import REDIS_CONFIG, REDIS_PASSWORD

# Channels Configuration
# https://channels.readthedocs.io/en/stable/topics/channel_layers.html

# Use Redis if Redis is configured (has password or explicit configuration)
# In development, Redis might be optional, so check if it's actually configured
# We check for REDIS_PASSWORD or if REDIS_CONFIG has hosts configured
use_redis = REDIS_PASSWORD is not None or (REDIS_CONFIG and REDIS_CONFIG.get("hosts"))

if use_redis:
    # Redis is configured (either via URL or individual parameters)
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": REDIS_CONFIG,
        },
    }
else:
    # Development: Use InMemoryChannelLayer when Redis is not configured
    # This allows development without Redis if desired
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    }

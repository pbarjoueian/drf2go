"""
Feature-specific settings modules.

Imported by ``config.settings.base`` at the end of the file so that each module
can rely on the core settings already being defined.
"""

from .celery_conf import *
from .channels_conf import *
from .cors_headers_conf import *
from .drf_conf import *
from .logging_conf import *
from .rabbitmq_conf import *
from .redis_conf import *
from .spectacular_conf import *

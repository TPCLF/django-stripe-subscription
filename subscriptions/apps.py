import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class SubscriptionsConfig(AppConfig):
    name = 'subscriptions'

    def ready(self):
        # Import signal handlers
        try:
            from . import signals  # noqa: F401
        except Exception as e:
            logger.error(f"Error importing subscriptions signals: {e}")

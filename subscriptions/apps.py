from django.apps import AppConfig


class SubscriptionsConfig(AppConfig):
    name = 'subscriptions'

    def ready(self):
        # Import signal handlers
        try:
            from . import signals  # noqa: F401
        except Exception as e:
            print(f"Error importing subscriptions signals: {e}")

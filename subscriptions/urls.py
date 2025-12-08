from django.urls import path
from . import views, views_alerts

urlpatterns = [
    path("", views.home, name="subscriptions-home"),
    path("create-checkout-session/", views.create_checkout_session),
    path("config/", views.stripe_config),
    path("success/", views.success),
    path("cancel/", views.cancel),
    path("webhook/", views.stripe_webhook),
    path("alerts/", views_alerts.alerts_view, name="alerts"),
    path("alerts/update/", views_alerts.update_alerts, name="update_alerts"),
    path("webhooks/storage/", views_alerts.storage_webhook, name="storage_webhook"),
]
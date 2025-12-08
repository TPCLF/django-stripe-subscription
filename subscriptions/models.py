from django.contrib.auth.models import User
from django.db import models
import uuid

class StripeCustomer(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    stripeCustomerId = models.CharField(max_length=255)
    stripeSubscriptionId = models.CharField(max_length=255)
    supabase_user_uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.user.username
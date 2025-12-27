#!/usr/bin/env python3
import os
import sys
import django

sys.path.insert(0, '/home/user/django-stripe-subscription')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostripe.settings')
django.setup()

from django.contrib.auth.models import User
from subscriptions.models import StripeCustomer
from subscriptions.utils import get_supabase_client
from django.conf import settings
from supabase import create_client

user = User.objects.first()
customer = StripeCustomer.objects.filter(user=user).first()
user_uuid = str(customer.supabase_user_uuid)

print("Testing with REGULAR client (as used in views_alerts.py):")
supabase = get_supabase_client()
response = supabase.table('alerts').select('keyword').eq('user_id', user_uuid).execute()
print(f"Keywords: {[item['keyword'] for item in response.data]}")

print("\nTesting with SERVICE client:")
service_key = settings.SUPABASE_SERVICE_KEY
supabase_service = create_client(settings.SUPABASE_URL, service_key)
response2 = supabase_service.table('alerts').select('keyword').eq('user_id', user_uuid).execute()
print(f"Keywords: {[item['keyword'] for item in response2.data]}")

#!/usr/bin/env python3
"""
Test script to compare regular vs service client for Supabase queries
Run with: python3 tests/test_double_check.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostripe.settings')
django.setup()

from django.contrib.auth.models import User
from subscriptions.models import StripeCustomer
from subscriptions.utils import get_supabase_client
from django.conf import settings
from supabase import create_client

user = User.objects.first()
if not user:
    print("ERROR: No users found in database")
    exit(1)

customer = StripeCustomer.objects.filter(user=user).first()
if not customer:
    print("ERROR: No StripeCustomer found for user")
    exit(1)

user_uuid = str(customer.supabase_user_uuid)

print("Testing with REGULAR client (as used in views_alerts.py):")
supabase = get_supabase_client()
response = supabase.table('alerts').select('keyword').eq('user_id', user_uuid).execute()
print(f"Keywords: {[item['keyword'] for item in response.data]}")

print("\nTesting with SERVICE client:")
service_key = settings.SUPABASE_SERVICE_KEY
if not service_key:
    print("ERROR: SUPABASE_SERVICE_KEY not configured")
    exit(1)

supabase_service = create_client(settings.SUPABASE_URL, service_key)
response2 = supabase_service.table('alerts').select('keyword').eq('user_id', user_uuid).execute()
print(f"Keywords: {[item['keyword'] for item in response2.data]}")

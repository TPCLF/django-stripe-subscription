#!/usr/bin/env python3
"""
Test script to verify Supabase service key operations
Run with: python3 tests/test_service_key.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostripe.settings')
django.setup()

from django.contrib.auth.models import User
from subscriptions.models import StripeCustomer
from django.conf import settings
from supabase import create_client

# Get user
user = User.objects.first()
if not user:
    print("ERROR: No users found in database")
    exit(1)

customer = StripeCustomer.objects.filter(user=user).first()
if not customer:
    print("ERROR: No StripeCustomer found for user")
    exit(1)

user_uuid = str(customer.supabase_user_uuid)
print(f"User UUID: {user_uuid}")

# Create service client
service_key = settings.SUPABASE_SERVICE_KEY
if not service_key:
    print("ERROR: SUPABASE_SERVICE_KEY not configured")
    exit(1)

supabase_service = create_client(settings.SUPABASE_URL, service_key)

# Try to insert test data
test_counties = ["Fulton", "DeKalb", "Cobb"]
print(f"\nInserting test counties: {test_counties}")

try:
    # Delete existing
    del_res = supabase_service.table('alerts').delete().eq('user_id', user_uuid).execute()
    print(f"Deleted: {len(del_res.data)} rows")

    # Insert new
    data = [{'user_id': user_uuid, 'keyword': c} for c in test_counties]
    ins_res = supabase_service.table('alerts').insert(data).execute()
    print(f"Inserted: {len(ins_res.data)} rows")

    # Verify
    response = supabase_service.table('alerts').select('keyword').eq('user_id', user_uuid).execute()
    keywords = [item['keyword'] for item in response.data]
    print(f"\nVerification - Keywords in database: {keywords}")
    print("\n✓ SUCCESS!")

except Exception as e:
    print(f"\n✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

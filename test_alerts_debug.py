#!/usr/bin/env python3
"""
Test script to verify alerts functionality
Run with: python3 test_alerts_debug.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/home/user/django-stripe-subscription')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostripe.settings')
django.setup()

from django.contrib.auth.models import User
from subscriptions.models import StripeCustomer
from subscriptions.utils import get_supabase_client

def test_alerts():
    print("=" * 60)
    print("TESTING ALERTS FUNCTIONALITY")
    print("=" * 60)
    
    # Get first user
    user = User.objects.first()
    if not user:
        print("ERROR: No users found in database")
        return
    
    print(f"\n1. Testing with user: {user.username}")
    print(f"   Email: {user.email}")
    
    # Get or create customer
    customer, created = StripeCustomer.objects.get_or_create(
        user=user,
        defaults={'stripeCustomerId': '', 'stripeSubscriptionId': ''}
    )
    
    print(f"\n2. StripeCustomer:")
    print(f"   Created new customer: {created}")
    print(f"   Customer ID: {customer.id}")
    print(f"   Supabase UUID: {customer.supabase_user_uuid}")
    print(f"   UUID Type: {type(customer.supabase_user_uuid)}")
    
    # Try to fetch alerts from Supabase
    try:
        supabase = get_supabase_client()
        user_uuid = str(customer.supabase_user_uuid)
        
        print(f"\n3. Querying Supabase:")
        print(f"   user_id: {user_uuid}")
        
        response = supabase.table('alerts').select('keyword').eq('user_id', user_uuid).execute()
        
        print(f"   Response status: {response}")
        print(f"   Response data: {response.data}")
        print(f"   Number of keywords: {len(response.data)}")
        
        user_keywords = [item['keyword'] for item in response.data]
        print(f"\n4. User Keywords List:")
        for kw in user_keywords:
            print(f"   - {kw}")
            
        if not user_keywords:
            print("\n   WARNING: No keywords found for this user!")
            print("   This explains why no checkboxes are checked.")
            
    except Exception as e:
        print(f"\nERROR querying Supabase: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_alerts()

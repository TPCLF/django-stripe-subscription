import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostripe.settings')
django.setup()

from django.contrib.auth.models import User
from subscriptions.models import StripeCustomer
from subscriptions.utils import get_supabase_client

# Get the first user
user = User.objects.first()
print(f"Testing with user: {user.username}")

# Get or create StripeCustomer
customer, created = StripeCustomer.objects.get_or_create(
    user=user,
    defaults={'stripeCustomerId': '', 'stripeSubscriptionId': ''}
)
print(f"StripeCustomer: {customer.supabase_user_uuid} (created: {created})")

# Test Supabase connection
try:
    supabase = get_supabase_client()
    print("Supabase client created")
    
    user_uuid = str(customer.supabase_user_uuid)
    
    # Try to insert a test alert
    test_data = [{'user_id': user_uuid, 'keyword': 'TestCounty'}]
    print(f"Attempting to insert: {test_data}")
    
    response = supabase.table('alerts').insert(test_data).execute()
    print(f"Insert response: {response}")
    
    # Try to read it back
    response = supabase.table('alerts').select('*').eq('user_id', user_uuid).execute()
    print(f"Read response: {response.data}")
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

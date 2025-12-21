
# Create Django users and StripeCustomer mappings for counties missing email mappings.
from django.contrib.auth.models import User
from subscriptions.models import StripeCustomer

# Map of county -> supabase_user_uuid (as observed in Supabase alerts)
county_uuid_map = {
    'Franklin': '98ddf211-5f2d-43d8-bd5b-2ed42b47b882',
    'Walker': '98ddf211-5f2d-43d8-bd5b-2ed42b47b882',
    'Wilkes': '98ddf211-5f2d-43d8-bd5b-2ed42b47b882',
    'Jackson': '33ff9822-60dc-4840-9d40-d78fea48fa67',
}

for county, uuid in county_uuid_map.items():
    username = county.lower()
    email = f"{username}@example.com"
    user, created = User.objects.get_or_create(username=username, defaults={'email': email})
    if created:
        user.set_password('testpass')
        user.save()
        print(f"Created user {username} ({email})")
    else:
        print(f"User {username} already exists")

    # Ensure a StripeCustomer exists and is mapped to this supabase UUID
    sc, sc_created = StripeCustomer.objects.get_or_create(user=user, defaults={'stripeCustomerId': '', 'stripeSubscriptionId': '', 'supabase_user_uuid': uuid})
    if sc_created:
        # If created, but supabase_user_uuid default might be random; set it to desired uuid
        sc.supabase_user_uuid = uuid
        sc.save()
        print(f"Created StripeCustomer for {username} -> {uuid}")
    else:
        # Update existing mapping if necessary
        if str(sc.supabase_user_uuid) != uuid:
            sc.supabase_user_uuid = uuid
            sc.save()
            print(f"Updated StripeCustomer for {username} -> {uuid}")
        else:
            print(f"StripeCustomer for {username} already mapped to {uuid}")

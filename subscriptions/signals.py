from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import receiver
import os

try:
    from allauth.account.signals import user_signed_up
except Exception:
    user_signed_up = None

@receiver(user_signed_up)
def send_welcome_email(request, user, **kwargs):
    """Send a welcome email when a user signs up via allauth and upsert the user into Supabase 'users' table.

    NOTE: We do NOT store plaintext passwords in Supabase. Only store email and identifiers for lookup.
    """
    try:
        subject = "Welcome to the Alerts App"
        message = f"Hi {user.username},\n\nThanks for signing up. You'll receive alerts when matching files are uploaded.\n\n- The Team"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
    except Exception as e:
        print(f"Welcome email error: {e}")

    # Upsert into Supabase users table
    try:
        service_key = getattr(settings, 'SUPABASE_SERVICE_KEY', '') or os.environ.get('SUPABASE_SERVICE_KEY', '')
        supabase_url = getattr(settings, 'SUPABASE_URL', '')
        if service_key and supabase_url:
            from supabase import create_client
            supabase = create_client(supabase_url, service_key)

            data = {
                'django_user_id': user.id,
                'email': user.email,
                'username': user.username,
            }

            # Upsert by email (requires 'email' to be unique in Supabase)
            try:
                supabase.table('users').upsert(data).execute()
                print(f"Upserted user into Supabase users table: {user.email}")
            except Exception as e:
                print(f"Supabase upsert error: {e}")
    except Exception as e:
        print(f"Error syncing user to Supabase: {e}")

# Add login sync handler
try:
    from allauth.account.signals import user_logged_in
except Exception:
    user_logged_in = None

@receiver(user_logged_in)
def sync_user_on_login(request, user, **kwargs):
    """Ensure the user exists in Supabase when they log in (keeps records in sync)."""
    try:
        service_key = getattr(settings, 'SUPABASE_SERVICE_KEY', '') or os.environ.get('SUPABASE_SERVICE_KEY', '')
        supabase_url = getattr(settings, 'SUPABASE_URL', '')
        if service_key and supabase_url:
            from supabase import create_client
            supabase = create_client(supabase_url, service_key)

            data = {
                'django_user_id': user.id,
                'email': user.email,
                'username': user.username,
            }
            try:
                supabase.table('users').upsert(data).execute()
                print(f"Upserted user on login into Supabase users table: {user.email}")
            except Exception as e:
                print(f"Supabase upsert error on login: {e}")
    except Exception as e:
        print(f"Error syncing user to Supabase on login: {e}")
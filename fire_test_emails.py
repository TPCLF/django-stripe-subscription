import os
import sys
import django
from django.conf import settings
from django.core.mail import send_mail

# Setup Django
sys.path.append('/home/user/django-stripe-subscription')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostripe.settings')
django.setup()

from django.contrib.auth.models import User

def fire_test_emails():
    print("Preparing to fire test emails...")
    
    # 1. Get or Create a Test User
    user, created = User.objects.get_or_create(
        username='testuser',
        email='testuser@example.com',
        defaults={'password': 'password123'}
    )
    if created:
        user.set_password('password123')
        user.save()
    
    print(f"Target User: {user.username} ({user.email})")

    # ==========================================
    # 1. Welcome Email
    # ==========================================
    print("\nSending Welcome Email...")
    subject = "Welcome to Georgia Auction Alert Archive!"
    body = f"""Dear {user.username},

We're thrilled to welcome you to our community here at GAAA! We hope you find just what you want at the next auction!

To get started, simply log in and click on the alerts button. Here, you can select your desired counties. Once you've saved your preferences, our system will send you timely alerts about upcoming auctions in your area.

Remember, we pay humans to do our data entry and human error could cause alerts not to come through from time to time for many reasons. So, check back at the web site before first Tuesday each month to make sure you dont miss anything!

Best Regards,
GAAA Admin Team
"""
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
        print(" -> Sent!")
    except Exception as e:
        print(f" -> ERROR: {e}")

    # ==========================================
    # 2. Subscription Paid Email (Renewed)
    # ==========================================
    print("\nSending Subscription Paid Email...")
    subject = "Your subscription is all paid up! You're good to go!"
    body = f"""Dear {user.username},

We just wanted to drop you a line and say thank you for your continued support! We're overjoyed to have you as part of our community.

Rest assured, your account is all paid up, please continue to expect your auction alerts and updates. We look forward to helping you find the perfect auction opportunities in your area. 

Stay tuned for more exciting auctions coming your way!

Best Regards,
GAAA Admin Team
"""
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
        print(" -> Sent!")
    except Exception as e:
        print(f" -> ERROR: {e}")

    # ==========================================
    # 3. Subscription Not Paid Email (Due)
    # ==========================================
    print("\nSending Subscription Due Email...")
    subject = "Attention: Your subscription is due."
    body = f"""Dear {user.username},

We hope you're enjoying our auction alert services! As a reminder, your subscription will expire shortly if it has not been renewed. To continue receiving updates and alerts about upcoming auctions in your area, please login to your account and update your billing information promptly.

Your participation is important to us, and we would hate to see you miss out on some exciting opportunities. We hope to see you back with us soon! 

If you encounter any issues or have questions about renewing your subscription, please don't hesitate to reach out to our support team at dev@example.com.

Wishing you the best,
GAAA Admin Team
"""
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
        print(" -> Sent!")
    except Exception as e:
        print(f" -> ERROR: {e}")

    # ==========================================
    # 4. Auction Alert Email
    # ==========================================
    print("\nSending Auction Alert Email...")
    
    # Mock Data
    filename = "Appling_02-14-2026_Auction.csv"
    county_name = "Appling"
    
    # Extract date logic (matching views_alerts.py)
    import re
    date_match = re.search(r'(\d{1,2}-\d{1,2}-\d{4})', filename)
    auction_date = date_match.group(1) if date_match else "Upcoming Tuesday"

    subject = "Exciting news! An auction is about to happen in an area you've expressed interest in!"
    body = f"""Hey {user.username},

An auction is happening soon in your selected area!

The auction is scheduled for Tuesday, {auction_date}, at 10am in {county_name} County.

Remember to keep an eye on your email and our website for more updates.

We wish you the best of luck at the auction!
GAAA Admin Team
"""
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email])
        print(" -> Sent!")
    except Exception as e:
        print(f" -> ERROR: {e}")
        
    print("\nDone! Please check MailHog at http://localhost:8025")

if __name__ == "__main__":
    fire_test_emails()

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.conf import settings
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import stripe

from django.contrib.auth.models import User
from django.http.response import JsonResponse, HttpResponse
from subscriptions.models import StripeCustomer
from django.core.mail import send_mail

from subscriptions.utils import list_files

def home(request):
    user_is_active = False
    subscription = None
    product = None
    
    if request.user.is_authenticated:
        try:
            stripe_customer = StripeCustomer.objects.get(user=request.user)
            stripe.api_key = settings.STRIPE_SECRET_KEY
            subscription = stripe.Subscription.retrieve(stripe_customer.stripeSubscriptionId)
            product = stripe.Product.retrieve(subscription.plan.product)
            
            # Check if subscription is active
            if subscription.status == 'active':
                user_is_active = True
                
        except StripeCustomer.DoesNotExist:
            pass
        except Exception as e:
            print(f"Error fetching subscription: {e}")

    # Allow any logged-in user to see all files
    can_see_all_files = request.user.is_authenticated
    files = list_files(user_is_active=can_see_all_files)

    return render(request, "home.html", {
        "subscription": subscription,
        "product": product,
        "files": files,
        "user_is_active": user_is_active,
        "can_see_all_files": can_see_all_files
    })

@csrf_exempt
def stripe_config(request):
    if request.method == "GET":
        stripe_config = {"publicKey": settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=True)



@csrf_exempt
def create_checkout_session(request):
    if request.method == "GET":
        domain_url = "http://localhost:8000/"
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                client_reference_id = request.user.id if request.user.is_authenticated else None,
                success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + "cancel/",
                payment_method_types= ["card"],
                mode = "subscription",
                line_items=[
                    {
                        "price": settings.STRIPE_PRICE_ID,
                        "quantity": 1,
                    }
                ]
            )
            return JsonResponse({"sessionId": checkout_session["id"]})
        except Exception as e:
            return JsonResponse({"error": str(e)})


@login_required
def success(request):
    return render(request, "success.html")

@login_required
def cancel(request):
    return render(request, "cancel.html")




def send_subscription_email(user, subject, message):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        print(f"Sent email to {user.email}: {subject}")
    except Exception as e:
        print(f"Error sending email to {user.email}: {e}")

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        # Fetch all the required data from session
        client_reference_id = session.get('client_reference_id')
        stripe_customer_id = session.get('customer')
        stripe_subscription_id = session.get("subscription")

        # Get the user and create a new StripeCustomer
        try:
            user = User.objects.get(id=client_reference_id)
            StripeCustomer.objects.create(
                user=user,
                stripeCustomerId=stripe_customer_id,
                stripeSubscriptionId=stripe_subscription_id,
            )
            print(user.username + " just subscribed.")
            
            # Send welcome email
            subject = "Welcome to Georgia Auction Alert Archive!"
            body = f"""Dear {user.username},

We're thrilled to welcome you to our community here at GAAA! We hope you find just what you want at the next auction!

To get started, simply log in and click on the alerts button. Here, you can select your desired counties. Once you've saved your preferences, our system will send you timely alerts about upcoming auctions in your area.

Remember, we pay humans to do our data entry and human error could cause alerts not to come through from time to time for many reasons. So, check back at the web site before first Tuesday each month to make sure you dont miss anything!

Best Regards,
GAAA Admin Team
"""
            send_subscription_email(user, subject, body)
        except User.DoesNotExist:
            print("User not found for checkout session.")

    elif event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        stripe_customer_id = invoice.get('customer')
        
        # We need to find the user associated with this customer ID
        try:
            customer = StripeCustomer.objects.get(stripeCustomerId=stripe_customer_id)
            user = customer.user
            
            # Check if this is a renewal 
            billing_reason = invoice.get('billing_reason')
            
            if billing_reason == 'subscription_cycle':
                print(f"Subscription renewed for {user.username}")
                subject = "Your subscription is all paid up! You're good to go!"
                body = f"""Dear {user.username},

We just wanted to drop you a line and say thank you for your continued support! We're overjoyed to have you as part of our community.

Rest assured, your account is all paid up, please continue to expect your auction alerts and updates. We look forward to helping you find the perfect auction opportunities in your area. 

Stay tuned for more exciting auctions coming your way!

Best Regards,
GAAA Admin Team
"""
                send_subscription_email(user, subject, body)
        except StripeCustomer.DoesNotExist:
            print(f"StripeCustomer not found for customer_id: {stripe_customer_id}")

    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        stripe_customer_id = invoice.get('customer')
        
        try:
            customer = StripeCustomer.objects.get(stripeCustomerId=stripe_customer_id)
            user = customer.user
            
            print(f"Payment failed for {user.username}")
            subject = "Attention: Your subscription is due."
            body = f"""Dear {user.username},

We hope you're enjoying our auction alert services! As a reminder, your subscription will expire shortly if it has not been renewed. To continue receiving updates and alerts about upcoming auctions in your area, please login to your account and update your billing information promptly.

Your participation is important to us, and we would hate to see you miss out on some exciting opportunities. We hope to see you back with us soon! 

If you encounter any issues or have questions about renewing your subscription, please don't hesitate to reach out to our support team at dev@example.com.

Wishing you the best,
GAAA Admin Team
"""
            send_subscription_email(user, subject, body)
        except StripeCustomer.DoesNotExist:
            print(f"StripeCustomer not found for customer_id: {stripe_customer_id}")

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        stripe_customer_id = subscription.get('customer')
        
        try:
            customer = StripeCustomer.objects.get(stripeCustomerId=stripe_customer_id)
            user = customer.user
            
            print(f"Subscription ended for {user.username}")
            # Optional: Send a final goodbye email or just log it. 
            # The user didn't explicitly ask for an "Ended" email different from "Not Paid", 
            # but "Not Paid" implies a chance to renew. 
            # I'll keep the previous simple logic for deleted or remove it if it conflicts.
            # I'll keep it simple.
            send_subscription_email(
                user,
                "Subscription Ended",
                f"Hi {user.username},\n\nYour subscription has ended. We hope to see you again soon!"
            )
        except StripeCustomer.DoesNotExist:
            print(f"StripeCustomer not found for customer_id: {stripe_customer_id}")

    return HttpResponse(status=200)
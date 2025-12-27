from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from .models import StripeCustomer
from .utils import get_supabase_client
import os
import json

# List of Georgia Counties
GA_COUNTIES = [
    "Appling", "Atkinson", "Bacon", "Baker", "Baldwin", "Banks", "Barrow", "Bartow", "Ben Hill", "Berrien",
    "Bibb", "Bleckley", "Brantley", "Brooks", "Bryan", "Bulloch", "Burke", "Butts", "Calhoun", "Camden",
    "Candler", "Carroll", "Catoosa", "Charlton", "Chatham", "Chattahoochee", "Chattooga", "Cherokee", "Clarke", "Clay",
    "Clayton", "Clinch", "Cobb", "Coffee", "Colquitt", "Columbia", "Cook", "Coweta", "Crawford", "Crisp",
    "Dade", "Dawson", "Decatur", "DeKalb", "Dodge", "Dooly", "Dougherty", "Douglas", "Early", "Echols",
    "Effingham", "Elbert", "Emanuel", "Evans", "Fannin", "Fayette", "Floyd", "Forsyth", "Franklin", "Fulton",
    "Gilmer", "Glascock", "Glynn", "Gordon", "Grady", "Greene", "Gwinnett", "Habersham", "Hall", "Hancock",
    "Haralson", "Harris", "Hart", "Heard", "Henry", "Houston", "Irwin", "Jackson", "Jasper", "Jeff Davis",
    "Jefferson", "Jenkins", "Johnson", "Jones", "Lamar", "Lanier", "Laurens", "Lee", "Liberty", "Lincoln",
    "Long", "Lowndes", "Lumpkin", "Macon", "Madison", "Marion", "McDuffie", "McIntosh", "Meriwether", "Miller",
    "Mitchell", "Monroe", "Montgomery", "Morgan", "Murray", "Muscogee", "Newton", "Oconee", "Oglethorpe", "Paulding",
    "Peach", "Pickens", "Pierce", "Pike", "Polk", "Pulaski", "Putnam", "Quitman", "Rabun", "Randolph",
    "Richmond", "Rockdale", "Schley", "Screven", "Seminole", "Spalding", "Stephens", "Stewart", "Sumter", "Talbot",
    "Taliaferro", "Tattnall", "Taylor", "Telfair", "Terrell", "Thomas", "Tift", "Toombs", "Towns", "Treutlen",
    "Troup", "Turner", "Twiggs", "Union", "Upson", "Walker", "Walton", "Ware", "Warren", "Washington",
    "Wayne", "Webster", "Wheeler", "White", "Whitfield", "Wilcox", "Wilkes", "Wilkinson", "Worth"
]

@login_required
def alerts_view(request):
    try:
        # Get or create StripeCustomer for this user
        customer, created = StripeCustomer.objects.get_or_create(
            user=request.user,
            defaults={'stripeCustomerId': '', 'stripeSubscriptionId': ''}
        )
        user_uuid = str(customer.supabase_user_uuid)
        
        print(f"[ALERTS DEBUG] User: {request.user.username}")
        print(f"[ALERTS DEBUG] Customer UUID: {user_uuid}")
        print(f"[ALERTS DEBUG] Customer created: {created}")
        
        # Use service role key for server-side reads (bypass RLS) when available
        service_key = getattr(settings, 'SUPABASE_SERVICE_KEY', '') or os.environ.get('SUPABASE_SERVICE_KEY', '')
        if service_key:
            from supabase import create_client as create_supabase_client
            supabase = create_supabase_client(settings.SUPABASE_URL, service_key)
            print("[ALERTS DEBUG] Using service role key for read")
        else:
            # Fall back to the regular client (may be blocked by RLS)
            supabase = get_supabase_client()
            print("[ALERTS DEBUG] Using regular client (may be blocked by RLS)")
        
        # Fetch existing alerts from Supabase
        response = supabase.table('alerts').select('keyword').eq('user_id', user_uuid).execute()
        
        print(f"[ALERTS DEBUG] Supabase response data: {response.data}")
        
        user_keywords = [item['keyword'] for item in response.data]
        
        print(f"[ALERTS DEBUG] User keywords: {user_keywords}")
        
    except Exception as e:
        print(f"[ALERTS ERROR] Error fetching alerts: {e}")
        import traceback
        traceback.print_exc()
        user_keywords = []

    return render(request, 'alerts.html', {
        'counties': GA_COUNTIES,
        'user_keywords': user_keywords
    })

@login_required
def update_alerts(request):
    if request.method == 'POST':
        try:
            # Get or create StripeCustomer for this user
            customer, created = StripeCustomer.objects.get_or_create(
                user=request.user,
                defaults={'stripeCustomerId': '', 'stripeSubscriptionId': ''}
            )
            user_uuid = str(customer.supabase_user_uuid)
            selected_keywords = request.POST.getlist('keywords')
            
            # Use service role key for server-side writes (bypass RLS) when available
            service_key = getattr(settings, 'SUPABASE_SERVICE_KEY', '') or os.environ.get('SUPABASE_SERVICE_KEY', '')
            if service_key:
                from supabase import create_client as create_supabase_client
                supabase_service = create_supabase_client(settings.SUPABASE_URL, service_key)
            else:
                # Fall back to the regular client (may be blocked by RLS)
                supabase_service = get_supabase_client()

            # 1. Delete existing alerts for this user
            del_res = supabase_service.table('alerts').delete().eq('user_id', user_uuid).execute()
            # 2. Insert new alerts
            if selected_keywords:
                data = [{'user_id': user_uuid, 'keyword': k} for k in selected_keywords]
                ins_res = supabase_service.table('alerts').insert(data).execute()
                # If insert failed due to RLS or other DB error, surface a clear message
                if getattr(ins_res, 'status_code', None) and ins_res.status_code >= 400:
                    print(f"Supabase insert failed: {ins_res}")
                    return JsonResponse({'status': 'error', 'message': str(ins_res)}, status=500)
                if isinstance(ins_res, dict) and ins_res.get('error'):
                    print(f"Supabase insert error: {ins_res}")
                    return JsonResponse({'status': 'error', 'message': ins_res.get('error')}, status=500)

            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            print(f"Error updating alerts: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'invalid method'}, status=405)

@csrf_exempt
def storage_webhook(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            # Supabase Storage webhook payload structure:
            # { "type": "INSERT", "table": "objects", "record": { "name": "filename.csv", "bucket_id": "csvs", ... } }
            
            record = payload.get('record', {})
            filename = record.get('name', '')
            bucket_id = record.get('bucket_id', '')
            
            if not filename or bucket_id != settings.SUPABASE_BUCKET:
                return HttpResponse(status=200) # Ignore irrelevant events
                
            print(f"New file uploaded: {filename}")
            
            # Check for matching keywords in alerts table
            supabase = get_supabase_client()
            
            # Use the Supabase service role key for server-side reads if available (bypasses RLS)
            from supabase import create_client as create_supabase_client
            service_key = getattr(settings, 'SUPABASE_SERVICE_KEY', '') or os.environ.get('SUPABASE_SERVICE_KEY', '')
            if service_key:
                supabase_service = create_supabase_client(settings.SUPABASE_URL, service_key)
            else:
                supabase_service = supabase

            # We need to find all alerts where the keyword is contained in the filename.
            # Supabase doesn't have a simple "reverse like" query easily accessible via client for this specific case
            # efficiently without a stored procedure, but we can fetch all unique keywords or 
            # iterate through keywords. 
            # BETTER APPROACH: Fetch all alerts, filter in Python (if dataset is small) 
            # OR use Supabase text search if configured.
            # Given the constraints, let's fetch alerts matching the counties.
            # Optimization: If we have many users, this is bad. 
            # Alternative: Extract potential keywords from filename (e.g. split by _) and query for those.
            
            # Heuristic: Check if any GA_COUNTY is in the filename
            matched_counties = [county for county in GA_COUNTIES if county.lower() in filename.lower()]
            
            if matched_counties:
                print(f"Matched counties: {matched_counties}")
                # Find users subscribed to these counties using the service client (no RLS)
                response = supabase_service.table('alerts').select('user_id').in_('keyword', matched_counties).execute()
                user_uuids = set(item['user_id'] for item in response.data) if response.data else set()
                
                for uuid_str in user_uuids:
                    customers = StripeCustomer.objects.filter(supabase_user_uuid=uuid_str)
                    if not customers.exists():
                        print(f"No StripeCustomer found for UUID {uuid_str}")
                        continue

                    for customer in customers:
                        user_email = customer.user.email
                        print(f"Sending alert to {user_email}")
                        result = send_mail(
                            subject=f"New Auction Alert: {filename}",
                            message=f"A new file matching your alerts has been uploaded: {filename}.\n\nLog in to view: http://localhost:8000/",
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[user_email],
                            fail_silently=True,
                        )
                        print(f"send_mail result: {result}")
                        
            return HttpResponse(status=200)
            
        except Exception as e:
            print(f"Webhook error: {e}")
            return HttpResponse(status=500)
            
    return HttpResponse(status=405)

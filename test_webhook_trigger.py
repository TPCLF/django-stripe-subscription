#!/usr/bin/env python3
"""
Test script to simulate a Supabase storage webhook call.
This helps test the email alert system without needing to actually upload files to Supabase.
"""

import requests
import json

# Configuration
WEBHOOK_URL = "http://localhost:8001/webhooks/storage/"

# Simulate a file upload webhook payload from Supabase
# This mimics what Supabase sends when a file is uploaded
test_payload = {
    "type": "INSERT",
    "table": "objects",
    "record": {
        "name": "Fulton-County-Auction-2024-12-08.csv",  # Change county name to test different keywords
        "bucket_id": "files",  # Should match SUPABASE_BUCKET in settings
        "owner": "test-user",
        "created_at": "2024-12-08T12:00:00Z"
    }
}

print("Testing webhook endpoint...")
print(f"URL: {WEBHOOK_URL}")
print(f"Payload: {json.dumps(test_payload, indent=2)}")
print("\n" + "="*60 + "\n")

try:
    response = requests.post(
        WEBHOOK_URL,
        json=test_payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        print("\n✓ Webhook processed successfully!")
        print("Check your Django server console for:")
        print("  - 'New file uploaded: ...'")
        print("  - 'Matched counties: ...'")
        print("  - 'Sending alert to ...'")
        print("  - Email content (if using console backend)")
    else:
        print(f"\n✗ Webhook failed with status {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("✗ ERROR: Could not connect to Django server")
    print("Make sure Django is running: python manage.py runserver 8001")
except Exception as e:
    print(f"✗ ERROR: {e}")

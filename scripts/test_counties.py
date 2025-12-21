import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangostripe.settings')
import django
django.setup()

from django.test import RequestFactory
from subscriptions.views_alerts import storage_webhook
import json, time, requests

rf = RequestFactory()
counties = ['Franklin', 'Walker', 'Wilkes', 'Jackson']

print('Starting county webhook tests...')
for c in counties:
    filename = f"{c}_2025-12-20.csv"
    payload = {'type': 'INSERT', 'table': 'objects', 'record': {'name': filename, 'bucket_id': 'csvs'}}
    req = rf.post('/webhooks/storage/', data=json.dumps(payload), content_type='application/json')
    print('---', c, '---')
    resp = storage_webhook(req)
    print('status', resp.status_code)
    time.sleep(0.5)

# Now check MailHog
mh = requests.get('http://127.0.0.1:8025/api/v2/messages').json()
items = mh.get('items', [])
found = []
for m in items:
    subj = m.get('Content', {}).get('Headers', {}).get('Subject', [''])[0]
    for c in counties:
        if c in subj and 'New Auction Alert' in subj:
            found.append({'county': c, 'subject': subj, 'to': m.get('Content', {}).get('Headers', {}).get('To', [None])[0]})

print('Found matches:', found)
print('Total messages in MailHog:', mh.get('total'))

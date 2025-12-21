import os
import time
from supabase import create_client
import requests

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SERVICE_KEY = os.environ.get('SRE_KEY')
USER_UUID = '42e302cc-3f97-4b5d-b8d9-f551de9142e4'  # admin user
KEYWORD = 'Fannin'

if not SUPABASE_URL or not SERVICE_KEY:
    print('Missing SUPABASE_URL or SRE_KEY env var')
    raise SystemExit(1)

supabase = create_client(SUPABASE_URL, SERVICE_KEY)

print('Inserting alert row...')
res = supabase.table('alerts').insert({'user_id': USER_UUID, 'keyword': KEYWORD}).execute()
print('Insert response status:', getattr(res, 'status_code', None) or getattr(res, 'status', None))
print('Insert response data:', res.data)

try:
    row_id = res.data[0].get('id') if res.data else None
except Exception:
    row_id = None

# Trigger webhook: simulate Supabase storage webhook for csv in csvs bucket
payload = {
    "type": "INSERT",
    "table": "objects",
    "record": {
        "name": f"{KEYWORD}_2025-12-08.csv",
        "bucket_id": os.environ.get('SUPABASE_BUCKET', 'csvs'),
        "owner": "test-user",
        "created_at": "2025-12-08T12:00:00Z"
    }
}

print('Posting webhook to local server...')
resp = requests.post('http://localhost:8001/webhooks/storage/', json=payload)
print('Webhook response status:', resp.status_code)

# Wait a moment and check MailHog
print('Waiting for email to be processed...')
time.sleep(1.5)

mh = requests.get('http://127.0.0.1:8025/api/v2/messages').json()
messages = mh.get('items', [])
found = []
for m in messages:
    subj = m.get('Content', {}).get('Headers', {}).get('Subject', [''])[0]
    if KEYWORD in subj or f"New Auction Alert" in subj:
        found.append({'id': m.get('ID'), 'subject': subj, 'to': m.get('Content', {}).get('Headers', {}).get('To')})

print('Found alert emails:', found)

# Clean up: delete the inserted row if we have id
if row_id:
    print('Deleting test row id', row_id)
    supabase.table('alerts').delete().eq('id', row_id).execute()
    print('Deleted')
else:
    print('No row id to delete; leaving inserted row as-is')

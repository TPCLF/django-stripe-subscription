import requests, re, os

BASE = 'http://127.0.0.1:8000'

# 1) GET signup page to obtain CSRF cookie
s = requests.Session()
r = s.get(BASE + '/accounts/signup/')
if r.status_code != 200:
    print('Failed to fetch signup page', r.status_code)
    raise SystemExit(1)

# Extract token from hidden input
m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.text)
if not m:
    print('CSRF token not found in signup page')
    raise SystemExit(1)
csrf = m.group(1)
print('CSRF token:', csrf)

# 2) POST to signup
payload = {
    'username': 'testsignup',
    'email': 'testsignup@example.com',
    'password1': 'testpass123',
    'password2': 'testpass123',
    'csrfmiddlewaretoken': csrf
}
headers = {'Referer': BASE + '/accounts/signup/'}
post = s.post(BASE + '/accounts/signup/', data=payload, headers=headers)
print('Signup POST status:', post.status_code)
if post.status_code in (302, 200):
    print('Signup likely succeeded (check DB)')
else:
    print('Signup failed. Response body starts:', post.text[:200])

# 3) Check MailHog for welcome message
mh = requests.get('http://127.0.0.1:8025/api/v2/messages').json()
items = mh.get('items', [])
welcome = [m for m in items if 'Welcome to the Alerts App' in (m.get('Content', {}).get('Headers', {}).get('Subject', [''])[0] or '')]
print('Welcome emails found in MailHog:', len(welcome))

# 4) Attempt login (use credentials) - first get CSRF token from login page
r2 = s.get(BASE + '/accounts/login/')
m2 = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r2.text)
if not m2:
    print('CSRF token not found in login page')
    raise SystemExit(1)
csrf2 = m2.group(1)
login_payload = {'login': 'testsignup', 'password': 'testpass123', 'csrfmiddlewaretoken': csrf2 }
headers = {'Referer': BASE + '/accounts/login/'}
login_resp = s.post(BASE + '/accounts/login/', data=login_payload, headers=headers)
print('Login POST status:', login_resp.status_code)
print('Login response URL (should redirect or land on homepage):', login_resp.url)

# Functional Changes - carter-contributions Branch

This document explains the functional changes made in this branch compared to `main`.

---

## Security Fixes

### 1. SECRET_KEY No Longer Hardcoded
**File:** `djangostripe/settings.py`

**Before:** Secret key was hardcoded directly in the source code, exposing it to anyone with repository access.
```python
SECRET_KEY = 'cq5pnv3l)3cigb9y%&lico@f6j!@8ma81m_@-(k7#074dp97+k'
```

**After:** Secret key is loaded from environment variable with a dev-only fallback.
```python
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-in-production")
```

**Why:** Hardcoded secrets in version control are a critical security vulnerability. Anyone with repo access could forge sessions or decrypt sensitive data.

---

### 2. DEBUG and ALLOWED_HOSTS Now Configurable
**File:** `djangostripe/settings.py`

**Before:** DEBUG was always True and ALLOWED_HOSTS was empty, making deployment insecure.
```python
DEBUG = True
ALLOWED_HOSTS = []
```

**After:** Both are configurable via environment variables.
```python
DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]
```

**Why:** Running DEBUG=True in production exposes detailed error pages with sensitive info. Empty ALLOWED_HOSTS with DEBUG=False causes Django to reject all requests.

---

### 3. Checkout Endpoint Now Requires Authentication
**File:** `subscriptions/views.py`

**Before:** Any visitor (authenticated or not) could access the checkout endpoint.
```python
@csrf_exempt
def create_checkout_session(request):
    ...
    client_reference_id = request.user.id if request.user.is_authenticated else None,
```

**After:** Login is required before accessing checkout.
```python
@login_required
@csrf_exempt
def create_checkout_session(request):
    ...
    client_reference_id = request.user.id,  # User is guaranteed authenticated
```

**Why:** Allowing anonymous checkout sessions creates orphaned Stripe customers that can't be linked to user accounts, causing billing confusion and potential fraud.

---

### 4. Fixed File Access Control Bug
**File:** `subscriptions/views.py`

**Before:** Any logged-in user could see all files, regardless of subscription status.
```python
# Allow any logged-in user to see all files
can_see_all_files = request.user.is_authenticated
```

**After:** Only active subscribers can see all files; others only see past-dated files.
```python
# Only active subscribers can see all files (non-subscribers see past files only)
can_see_all_files = user_is_active
```

**Why:** This was a paywall bypass bug. Users could sign up for a free account and access premium content without subscribing.

---

### 5. Hardcoded Domain URL Removed
**File:** `subscriptions/views.py`

**Before:** Checkout URLs were hardcoded to localhost, breaking production deployments.
```python
domain_url = "http://localhost:8000/"
```

**After:** Domain URL is built dynamically from the request.
```python
domain_url = request.build_absolute_uri("/")
```

**Why:** Hardcoded localhost URLs cause Stripe redirects to fail in production, breaking the entire payment flow.

---

### 6. Webhook Endpoint Hardened
**File:** `subscriptions/views.py`

**Before:** Webhook could crash if signature header was missing; no validation of endpoint secret.
```python
sig_header = request.META["HTTP_STRIPE_SIGNATURE"]  # KeyError if missing
```

**After:** Safe header retrieval with validation.
```python
# Validate webhook secret is configured
if not endpoint_secret:
    print("ERROR: STRIPE_ENDPOINT_SECRET not configured")
    return HttpResponse(status=500)

# Get signature header safely
sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
if not sig_header:
    return HttpResponse(status=400)
```

**Why:** Missing signature header would cause a 500 error and expose stack trace. Missing endpoint secret means webhooks can't be verified, allowing forged events.

---

### 7. CSRF Cookie Protection Enabled
**File:** `djangostripe/settings.py`

**Before:** CSRF cookie was accessible to JavaScript.
```python
CSRF_COOKIE_HTTPONLY = False
```

**After:** CSRF cookie is HTTP-only.
```python
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access to CSRF cookie
```

**Why:** If an XSS vulnerability exists, attackers could steal the CSRF token and perform cross-site request forgery attacks.

---

### 8. Production Cookie Security Added
**File:** `djangostripe/settings.py`

**New:** When DEBUG=False, cookies are only sent over HTTPS.
```python
# Production security (enabled when DEBUG=False)
if not DEBUG:
    SESSION_COOKIE_SECURE = True  # Only send cookies over HTTPS
    CSRF_COOKIE_SECURE = True     # Only send CSRF cookie over HTTPS
    SECURE_SSL_REDIRECT = True    # Redirect HTTP to HTTPS
```

**Why:** Without these settings, session cookies could be intercepted over unencrypted connections, enabling session hijacking.

---

## Bug Fixes

### 9. Missing `import sys` Added
**File:** `subscriptions/utils.py`

**Before:** Code referenced `sys.stderr` but `sys` was not imported, causing crashes when Supabase credentials were missing.

**After:** Added `import sys` at the top of the file.

**Why:** Without this import, the fallback to mock Supabase client would crash, breaking the entire file listing feature.

---

### 10. CSRF Trusted Origins Now Extensible
**File:** `djangostripe/settings.py`

**Before:** Only hardcoded localhost origins were trusted.

**After:** Production domains can be added via environment variable.
```python
_csrf_origins = os.environ.get("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8001",
    ...
] + [o.strip() for o in _csrf_origins.split(",") if o.strip()]
```

**Why:** Without this, POST requests from production domains would fail CSRF validation.

---

## Compatibility Updates

### 11. django-allauth Middleware Added
**File:** `djangostripe/settings.py`

**New:** Added required middleware for django-allauth 65+.
```python
MIDDLEWARE = [
    ...
    # Required for django-allauth 65+
    "allauth.account.middleware.AccountMiddleware",
]
```

**Why:** The updated django-allauth package requires this middleware or the app crashes on startup.

---

### 12. Default Auto Field Configured
**File:** `djangostripe/settings.py`

**New:** Silences Django 3.2+ warning about auto-generated primary keys.
```python
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

**Why:** Without this, Django emits warnings for every model without an explicit primary key field.

---

### 13. Requirements Updated for Python 3.13
**File:** `requirements.txt`

All dependencies updated to Python 3.13-compatible versions:
- Django 5.2.10 (LTS)
- django-allauth 65.13.1
- stripe 14.1.0
- supabase 2.27.2
- And others...

**Why:** Original requirements were incompatible with Python 3.13 (setuptools import errors).

---

## New Files Added

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Development guidelines and architecture overview |
| `README.md` | Comprehensive project documentation |
| `.env.example` | Template for environment variables |
| `.github/workflows/ci.yml` | GitHub Actions for testing |
| `.github/workflows/deploy.yml` | Tag-based deployment to Railway |
| `CLAUDE_FINDINGS.md` | Full code review findings |
| `supabase/config.toml` | Local Supabase configuration |

---

## Files Removed

| File | Reason |
|------|--------|
| `stripe` | Binary file (21MB) - should not be in repo |
| `stripe.tar.gz` | Archive (7.6MB) - should not be in repo |
| Binary file with control character | Corrupted/accidental file |

---

## Summary

**Critical Security Issues Fixed:** 4
- Hardcoded SECRET_KEY
- Unauthenticated checkout access
- File access control bypass
- Hardcoded domain URL

**High Priority Security Issues Fixed:** 4
- DEBUG/ALLOWED_HOSTS configuration
- Webhook validation
- CSRF cookie protection
- Production cookie security

**Bug Fixes:** 2
- Missing import
- CSRF origins configuration

**Compatibility Updates:** 3
- django-allauth middleware
- Default auto field
- Python 3.13 requirements

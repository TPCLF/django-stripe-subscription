from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import get_token

class EnsureCSRFCookieMiddleware(MiddlewareMixin):
    """Ensure a CSRF cookie is set on safe (GET/HEAD) requests so browser signups/logins get a cookie.

    This avoids 'CSRF cookie not set' errors for first-time visitors who use the signup/login forms.
    """
    def process_request(self, request):
        # Only ensure token for safe methods and for pages that may present forms
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            # get_token will ensure a cookie is set
            try:
                get_token(request)
            except Exception:
                # Don't fail the request if token generation fails
                pass
        return None

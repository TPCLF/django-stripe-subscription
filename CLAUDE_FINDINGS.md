Ready to code?

 Here is Claude's plan:
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 Code Review: Georgia Auction Alert Archive (GAAA)

 Executive Summary

 This Django SaaS application has multiple critical issues that must be addressed before production deployment. The codebase is functional for development but requires significant security hardening, bug fixes, and code quality
 improvements.

 Risk Level: HIGH - Not production-ready in current state.

 ---
 Critical Issues (Must Fix Immediately)

 1. Hardcoded SECRET_KEY (CRITICAL)

 - File: djangostripe/settings.py:27
 - Issue: SECRET_KEY = 'cq5pnv3l)3cigb9y%&lico@f6j!@8ma81m_@-(k7#074dp97+k'
 - Impact: Anyone with repo access can forge sessions, CSRF tokens, password reset links
 - Fix: Move to environment variable, rotate immediately

 2. Missing sys Import - Application Crash (CRITICAL)

 - File: subscriptions/utils.py:10
 - Issue: Uses sys.stderr but sys is not imported
 - Impact: Application crashes when Supabase credentials are missing
 - Fix: Add import sys at top of file

 3. DEBUG=True and Empty ALLOWED_HOSTS (CRITICAL)

 - File: djangostripe/settings.py:30,32
 - Issue: DEBUG = True and ALLOWED_HOSTS = [] hardcoded
 - Impact: Stack traces exposed, host header injection attacks possible
 - Fix: Use environment variables

 4. Hardcoded Domain URL (HIGH)

 - File: subscriptions/views.py:61
 - Issue: domain_url = "http://localhost:8000/" hardcoded
 - Impact: Stripe checkout fails in production, no HTTPS
 - Fix: Use environment variable or request.build_absolute_uri()

 5. Incorrect File Access Control (HIGH)

 - File: subscriptions/views.py:39
 - Issue: can_see_all_files = request.user.is_authenticated instead of checking subscription
 - Impact: Non-subscribers can see all files (breaks business model)
 - Fix: Change to can_see_all_files = user_is_active

 6. No Webhook Authentication for Supabase (HIGH)

 - File: subscriptions/views_alerts.py:120
 - Issue: @csrf_exempt webhook accepts any payload without signature verification
 - Impact: Attackers can trigger mass email spam via fake webhooks
 - Fix: Implement Supabase webhook signature validation

 ---
 Security Issues

 | Issue                         | Severity | File:Line           | Status     |
 |-------------------------------|----------|---------------------|------------|
 | Hardcoded SECRET_KEY          | CRITICAL | settings.py:27      | Unresolved |
 | Missing sys import (crash)    | CRITICAL | utils.py:10         | Unresolved |
 | DEBUG=True hardcoded          | CRITICAL | settings.py:30      | Unresolved |
 | ALLOWED_HOSTS empty           | CRITICAL | settings.py:32      | Unresolved |
 | Hardcoded localhost URL       | HIGH     | views.py:61         | Unresolved |
 | Wrong file access control     | HIGH     | views.py:39         | Unresolved |
 | No Supabase webhook auth      | HIGH     | views_alerts.py:120 | Unresolved |
 | CSRF_COOKIE_HTTPONLY=False    | HIGH     | settings.py:197     | Unresolved |
 | No auth on checkout endpoint  | HIGH     | views.py:58         | Unresolved |
 | SQLite in production          | HIGH     | settings.py:88      | Unresolved |
 | Missing webhook secret check  | HIGH     | views.py:109        | Unresolved |
 | Missing security headers      | MEDIUM   | settings.py         | Unresolved |
 | SESSION_COOKIE_SECURE missing | MEDIUM   | settings.py         | Unresolved |
 | No logging configuration      | MEDIUM   | settings.py         | Unresolved |

 ---
 Code Quality Issues

 Database & Models

 - Missing indexes: stripeCustomerId and stripeSubscriptionId need db_index=True
 - Missing unique constraints: Stripe IDs should have unique=True
 - Missing timestamps: No created_at/updated_at fields
 - camelCase fields: Should be snake_case (PEP 8 violation)
 - No subscription status cache: Every page load queries Stripe API

 Error Handling

 - Print statements everywhere: Should use Python logging
 - Inconsistent fail_silently: Email sending uses different patterns
 - Bare exception handlers: except Exception catches too broadly
 - Debug prints in production: 7+ [ALERTS DEBUG] statements in views_alerts.py

 Code Duplication (DRY Violations)

 - Supabase client initialization repeated 3x in views_alerts.py
 - Email sending code repeated 4x in views.py
 - Customer lookup by Stripe ID repeated 3x in webhook handler

 Dependencies (requirements.txt)

 | Package       | Current     | Status                     |
 |---------------|-------------|----------------------------|
 | Django        | 3.1.4       | OUTDATED (4.2+ available)  |
 | cryptography  | 3.3.1       | SECURITY RISK (known CVEs) |
 | stripe        | 2.55.1      | OUTDATED (7.0+ available)  |
 | urllib3       | 1.26.2      | OUTDATED                   |
 | supabase      | unversioned | Should pin version         |
 | python-dotenv | unversioned | Should pin version         |

 Tests

 - File: subscriptions/tests.py is EMPTY
 - No unit tests, integration tests, or webhook tests
 - No way to catch regressions

 ---
 Business Logic Issues

 County Matching Bug

 - File: subscriptions/views_alerts.py:159
 - Issue: Partial string matching - "Clark" matches "Clarkston"
 - Impact: Wrong alerts sent to users
 - Fix: Use word boundary matching

 Alert Access Not Checked

 - File: subscriptions/views_alerts.py:32
 - Issue: Non-subscribers can set alert preferences
 - Impact: Wasted storage, confusing UX

 No Unsubscribe Links

 - File: subscriptions/views_alerts.py:210
 - Issue: Emails have no unsubscribe mechanism
 - Impact: CAN-SPAM/GDPR violation risk

 User Deletion Not Handled

 - Issue: No signal to clean up Supabase when Django user deleted
 - Impact: Orphaned data in Supabase

 ---
 Recommended Fix Priority

 Phase 1: Critical Security (Immediate)

 1. Add import sys to utils.py
 2. Move SECRET_KEY to environment variable
 3. Move DEBUG and ALLOWED_HOSTS to environment variables
 4. Fix hardcoded domain_url in views.py
 5. Fix file access control (line 39)
 6. Add Supabase webhook signature validation

 Phase 2: High Priority Security

 1. Add @login_required to create_checkout_session
 2. Set CSRF_COOKIE_HTTPONLY=True
 3. Add webhook endpoint secret validation
 4. Configure security headers (HSTS, CSP, etc.)
 5. Add SESSION_COOKIE_SECURE for production

 Phase 3: Code Quality

 1. Replace all print() with proper logging
 2. Update requirements.txt (especially cryptography)
 3. Add database indexes to model
 4. Extract duplicate code to helpers
 5. Move email templates to files

 Phase 4: Business Logic

 1. Fix county matching to use word boundaries
 2. Check subscription status before allowing alerts
 3. Add unsubscribe links to emails
 4. Add user deletion signal for Supabase cleanup

 Phase 5: Testing & Polish

 1. Write tests for webhook handlers
 2. Write tests for Supabase integration
 3. Add proper model timestamps
 4. Cache subscription status locally

 ---
 Files Requiring Changes

 | File                          | Changes Needed                                    |
 |-------------------------------|---------------------------------------------------|
 | djangostripe/settings.py      | Environment variables, security headers, logging  |
 | subscriptions/utils.py        | Add import sys                                    |
 | subscriptions/views.py        | Fix access control, domain URL, add auth, logging |
 | subscriptions/views_alerts.py | Webhook auth, fix county matching, logging        |
 | subscriptions/models.py       | Add indexes, timestamps, unique constraints       |
 | subscriptions/signals.py      | Add user deletion handler                         |
 | requirements.txt              | Update all packages, pin versions                 |
 | subscriptions/tests.py        | Write actual tests                                |

 ---
 Positive Findings

 - Stripe webhook signature verification is properly implemented
 - Django ORM prevents SQL injection
 - Template auto-escaping prevents XSS
 - CSRF middleware is enabled
 - Authentication decorators used appropriately on most views
 - Good separation between views.py and views_alerts.py

# CLAUDE.md - Project Instructions

## Project Overview

**Georgia Auction Alert Archive (GAAA)** is a Django SaaS application that provides Georgia real estate auction alerts to subscribers. Users pay via Stripe subscriptions and receive email notifications when new auction files are uploaded for their selected counties.

## Tech Stack

- **Framework**: Django 3.1.4
- **Auth**: django-allauth (email/password, social auth)
- **Payments**: Stripe (subscriptions, webhooks)
- **Backend Storage**: Supabase (file storage + alerts database)
- **Database**: SQLite3 (dev), PostgreSQL recommended for production
- **Frontend**: Bootstrap 4.5.2, jQuery, Stripe.js

## Project Structure

```
djangostripe/          # Django project settings
  settings.py          # Main config (Stripe, Supabase, Email)
  urls.py              # Root URL routing

subscriptions/         # Main app
  models.py            # StripeCustomer model
  views.py             # Stripe checkout, webhooks, pages
  views_alerts.py      # Alert preferences, Supabase webhook
  utils.py             # Supabase client, file listing
  signals.py           # User signup/login hooks
  middleware.py        # CSRF cookie middleware

templates/             # Django templates
static/                # Static files (JS, CSS, images)
```

## Key Files

| File | Purpose |
|------|---------|
| `subscriptions/views.py:107` | Stripe webhook handler |
| `subscriptions/views.py:59` | Checkout session creation |
| `subscriptions/views_alerts.py` | County alert management |
| `subscriptions/utils.py` | Supabase file listing |
| `subscriptions/signals.py` | User sync to Supabase on signup/login |

## Development Commands

```bash
# Start dev server
python manage.py runserver 8000

# Run migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Create superuser for admin
python manage.py createsuperuser

# Django shell
python manage.py shell

# Check for issues
python manage.py check
```

## Environment Variables

Required in `.env`:

```bash
# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_ENDPOINT_SECRET=whsec_...
STRIPE_PRICE_ID=price_...

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...          # anon key
SUPABASE_SERVICE_KEY=eyJ...  # service role key
SUPABASE_BUCKET=files

# Email (optional - defaults to localhost:1025 for MailHog)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
```

## Stripe Integration Patterns

### Webhook Events Handled
- `checkout.session.completed` - Creates StripeCustomer, sends welcome email
- `invoice.payment_succeeded` - Sends renewal confirmation
- `invoice.payment_failed` - Sends payment failure alert
- `customer.subscription.deleted` - Sends cancellation notice

### Testing Webhooks Locally
Use ngrok to expose localhost:
```bash
ngrok http 8000
# Update STRIPE_ENDPOINT_SECRET with ngrok webhook secret
```

## Supabase Integration

- **File Storage**: Files uploaded to bucket trigger webhook to `/webhooks/storage/`
- **Alerts Table**: Stores user county preferences (user_id UUID, keyword text)
- **RLS**: Row-level security enabled; service key bypasses for server-side ops

## Email Testing

For local development, use MailHog:
```bash
# Install and run MailHog
mailhog
# View emails at http://localhost:8025
# SMTP on localhost:1025 (default in settings)
```

## Important Notes

- `domain_url` in `views.py:61` is hardcoded to localhost - needs env var for production
- `SECRET_KEY` in settings is hardcoded - must be env var for production
- `DEBUG = True` - must be False in production
- `ALLOWED_HOSTS = []` - must be configured for production

## Code Style

- Follow PEP 8
- Use Django conventions for views, models, URLs
- Keep webhook handlers in views.py
- Use signals.py for user lifecycle events

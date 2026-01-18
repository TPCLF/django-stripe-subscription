# Georgia Auction Alert Archive (GAAA)

A Django SaaS application that sends email alerts to subscribers about Georgia real estate auctions. Users subscribe via Stripe and select counties to receive notifications when new auction files are uploaded.

## Features

- Stripe subscription payments
- Email alerts for selected Georgia counties (all 159)
- Supabase file storage integration
- User authentication with django-allauth
- Webhook-triggered notifications

## Tech Stack

- **Backend**: Django 3.1.4, Python 3.8+
- **Auth**: django-allauth
- **Payments**: Stripe
- **Storage**: Supabase
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: Bootstrap 4.5, jQuery

---

## Local Development Setup

### Prerequisites

- Python 3.8+
- pip
- Git
- (Optional) MailHog for email testing
- (Optional) ngrok for Stripe webhook testing

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd django-stripe-subscription

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Stripe (see Stripe Setup section below)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_ENDPOINT_SECRET=whsec_...
STRIPE_PRICE_ID=price_...

# Supabase (see Supabase Setup section below)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIs...
SUPABASE_BUCKET=files

# Email (optional - defaults to MailHog localhost:1025)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### 3. Initialize Database

```bash
python manage.py migrate
python manage.py createsuperuser  # Optional: create admin user
```

### 4. Run Development Server

```bash
python manage.py runserver 8000
```

Visit http://localhost:8000

### 5. (Optional) Email Testing with MailHog

```bash
# Install MailHog (macOS)
brew install mailhog

# Or download from https://github.com/mailhog/MailHog/releases

# Run MailHog
mailhog
```

- SMTP: `localhost:1025` (default in settings)
- Web UI: http://localhost:8025

---

## Stripe Setup

### 1. Create a Stripe Account

1. Go to [stripe.com](https://stripe.com) and create an account
2. Verify your email

### 2. Get API Keys

1. Go to **Developers > API keys** in the Stripe Dashboard
2. Copy your **Publishable key** (`pk_test_...`) and **Secret key** (`sk_test_...`)
3. Add them to your `.env` file

### 3. Create a Product and Price

1. Go to **Products** in Stripe Dashboard
2. Click **+ Add product**
3. Fill in:
   - **Name**: "GAAA Monthly Subscription" (or your preferred name)
   - **Pricing model**: Recurring
   - **Price**: Your monthly price (e.g., $9.99)
   - **Billing period**: Monthly
4. Click **Save product**
5. Click on the product, find the **Price ID** (starts with `price_...`)
6. Add it to your `.env` as `STRIPE_PRICE_ID`

### 4. Configure Webhooks

#### For Local Development (using ngrok)

1. Install ngrok: https://ngrok.com/download
2. Start your Django server: `python manage.py runserver 8000`
3. In another terminal: `ngrok http 8000`
4. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
5. In Stripe Dashboard, go to **Developers > Webhooks**
6. Click **+ Add endpoint**
7. Enter your endpoint URL: `https://abc123.ngrok.io/webhook/`
8. Select events to listen:
   - `checkout.session.completed`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `customer.subscription.deleted`
9. Click **Add endpoint**
10. Click on the webhook, then **Reveal** the signing secret
11. Add it to `.env` as `STRIPE_ENDPOINT_SECRET`

#### For Production

Same steps as above, but use your production domain:
- Endpoint URL: `https://yourdomain.com/webhook/`

### 5. Test the Integration

1. Start your server and ngrok
2. Create an account on your app
3. Click "Subscribe" and use Stripe test card: `4242 4242 4242 4242`
4. Any expiry date in the future, any CVC
5. Check that:
   - You're redirected to success page
   - Welcome email is sent (check MailHog)
   - Subscription shows in Stripe Dashboard

---

## Supabase Setup

### 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and create an account
2. Create a new project
3. Note your **Project URL** and **API keys** (anon and service_role)

### 2. Create Storage Bucket

1. Go to **Storage** in Supabase Dashboard
2. Create a new bucket called `files` (or your preferred name)
3. Set appropriate policies (public read if needed)

### 3. Create Alerts Table

Run this SQL in Supabase SQL Editor:

```sql
CREATE TABLE alerts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
    keyword TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own alerts
CREATE POLICY "Users can view own alerts" ON alerts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own alerts" ON alerts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own alerts" ON alerts
    FOR DELETE USING (auth.uid() = user_id);
```

### 4. Configure Storage Webhook (Optional)

To trigger alerts when files are uploaded:

1. Go to **Database > Webhooks** in Supabase
2. Create a webhook on `storage.objects` INSERT events
3. Point it to `https://yourdomain.com/webhooks/storage/`

### 5. Add Keys to Environment

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_BUCKET=files
```

---

## Deployment

### Recommended: Railway

[Railway](https://railway.app) provides simple Django hosting with GitHub integration.

#### Initial Setup

1. Create a Railway account at [railway.app](https://railway.app)
2. Create a new project
3. Add a **PostgreSQL** database (optional but recommended for production)
4. Add a **Web Service** from your GitHub repo

#### Environment Variables

In Railway dashboard, add all variables from your `.env` file plus:

```bash
# Production settings
DEBUG=False
SECRET_KEY=your-secure-random-key
ALLOWED_HOSTS=your-app.railway.app,yourdomain.com
```

#### Create Project Token for CI/CD

1. Go to your project **Settings > Tokens**
2. Create a new token
3. Add it to GitHub repo secrets as `RAILWAY_TOKEN`

### GitHub Actions CI/CD

This project includes two GitHub Actions workflows:

#### CI Workflow (`.github/workflows/ci.yml`)
- Runs on every push and PR to `main`
- Checks Django configuration
- Validates migrations

#### Deploy Workflow (`.github/workflows/deploy.yml`)
- Triggers when you push a version tag (e.g., `v1.0.0`)
- Deploys to Railway

#### Releasing a New Version

```bash
# Make sure all changes are committed
git add .
git commit -m "Your changes"
git push origin main

# Create and push a version tag to trigger deploy
git tag v1.0.0
git push origin v1.0.0
```

---

## Production Checklist

Before deploying to production, ensure:

- [ ] `DEBUG = False` in settings (use env var)
- [ ] `SECRET_KEY` is set via environment variable (generate a new secure key)
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] Database is PostgreSQL (not SQLite)
- [ ] Stripe webhook uses production endpoint secret
- [ ] Email is configured with real SMTP provider
- [ ] `domain_url` in `subscriptions/views.py` uses environment variable
- [ ] SSL/HTTPS is enabled (required for Stripe webhooks)
- [ ] CSRF_TRUSTED_ORIGINS includes your production domain

### Generate a Secure SECRET_KEY

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page with files list |
| `/accounts/login/` | GET/POST | User login |
| `/accounts/signup/` | GET/POST | User registration |
| `/config/` | GET | Returns Stripe publishable key |
| `/create-checkout-session/` | GET | Creates Stripe checkout session |
| `/success/` | GET | Post-checkout success page |
| `/cancel/` | GET | Checkout cancelled page |
| `/webhook/` | POST | Stripe webhook endpoint |
| `/alerts/` | GET | County selection page |
| `/alerts/update/` | POST | Save alert preferences |

---

## Testing

```bash
# Run Django checks
python manage.py check

# Check migrations
python manage.py makemigrations --check --dry-run

# Run tests (if available)
python manage.py test
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests and checks
5. Commit: `git commit -m "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request

---

## License

[Add your license here]

# Test Scripts

Development and debugging scripts for testing various integrations.

## Prerequisites

- Django environment configured (`.env` file with credentials)
- Virtual environment activated
- At least one user in the database

## Scripts

| Script | Purpose |
|--------|---------|
| `test_alerts_debug.py` | Debug alerts functionality for a user |
| `test_alerts_save.py` | Test saving alerts to Supabase |
| `test_double_check.py` | Compare regular vs service client queries |
| `test_service_key.py` | Test Supabase service key operations |
| `test_supabase_connection.py` | Verify Supabase connection and bucket access |
| `test_webhook_trigger.py` | Simulate Supabase storage webhook |

## Usage

Run from the project root:

```bash
# Activate virtual environment
source venv/bin/activate

# Run a test
python tests/test_alerts_debug.py
```

## Notes

- These are development/debugging scripts, not automated unit tests
- All credentials are loaded from environment variables
- The webhook trigger test requires Django to be running

from unittest.mock import MagicMock
from datetime import datetime, timedelta

def get_mock_supabase_client():
    mock_client = MagicMock()
    
    today = datetime.now().date()
    past_date = today - timedelta(days=10)
    future_date = today + timedelta(days=10)
    
    mock_files = [
        {'name': f'report_{past_date}.csv'},
        {'name': f'report_{future_date}.csv'},
        {'name': 'no_date.csv'}
    ]
    
    mock_storage = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.list.return_value = mock_files
    mock_bucket.create_signed_url.return_value = "http://example.com/file.csv"
    
    mock_storage.from_.return_value = mock_bucket
    mock_client.storage = mock_storage
    
    return mock_client

import os
from datetime import datetime
from django.conf import settings
from supabase import create_client, Client

def get_supabase_client() -> Client:
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY
    if not url or not key:
        print("DEBUG: Credentials missing, using MOCK Supabase client", file=sys.stderr)
        from subscriptions.mock_supabase import get_mock_supabase_client
        return get_mock_supabase_client()
    return create_client(url, key)

def list_files(user_is_active=False):
    """
    List files from Supabase bucket.
    
    If user_is_active is True: return all files.
    If user_is_active is False: return only files with past dates.
    
    Assumes filename format contains date YYYY-MM-DD.
    """
    supabase = get_supabase_client()
    bucket_name = settings.SUPABASE_BUCKET
    
    try:
        # List all files in the bucket
        res = supabase.storage.from_(bucket_name).list()
        
        # res is a list of dictionaries, e.g., {'name': '...', 'id': '...', ...}
        
        files = []
        today = datetime.now().date()
        
        for file_obj in res:
            filename = file_obj.get('name')
            if not filename:
                continue
                
            # Attempt to extract date from filename
            # Simple heuristic: look for YYYY-MM-DD pattern
            # We can iterate through the filename to find a date match
            # Or assume a specific format. Let's try to find a date pattern.
            
            file_date = None
            try:
                # This is a basic extraction, might need refinement based on exact filename format
                # Let's assume the date is somewhere in the string in ISO format
                import re
                match = re.search(r'\d{4}-\d{2}-\d{2}', filename)
                if match:
                    date_str = match.group(0)
                    file_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
            
            if file_date:
                is_future = file_date > today
                
                if user_is_active or not is_future:
                    files.append({
                        'name': filename,
                        'date': file_date,
                        'is_future': is_future,
                        # Generate a signed URL for download/viewing if needed, or just public URL
                        # For now, let's just assume we list them. 
                        # If we need to download, we might need to generate a signed URL.
                        # Let's add a public url for now if the bucket is public, or signed if private.
                        # Assuming public for simplicity unless specified otherwise, but signed is safer.
                        # Let's generate a signed URL valid for 1 hour.
                        'url': supabase.storage.from_(bucket_name).create_signed_url(filename, 3600)
                    })
        
        # Sort by date descending (newest first)
        files.sort(key=lambda x: x['date'], reverse=True)
        return files
        
    except Exception as e:
        print(f"Error listing files from Supabase: {e}")
        return []

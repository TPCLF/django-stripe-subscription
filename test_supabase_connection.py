import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
bucket = os.environ.get("SUPABASE_BUCKET")

print(f"URL: {url}")
# print(f"KEY: {key}") # Don't print secret key
print(f"BUCKET: {bucket}")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not set in .env")
    exit(1)

try:
    supabase = create_client(url, key)
    print("Client created.")
    
    print("Listing all buckets:")
    buckets = supabase.storage.list_buckets()
    for b in buckets:
        print(f" - {b.name}")
    
    print(f"Attempting to list files in bucket '{bucket}'...")
    res = supabase.storage.from_(bucket).list()
    print(f"Response: {res}")
    
    if not res:
        print("Warning: Received empty list. Check if bucket exists, has files, and policies allow SELECT.")
    else:
        print("Files found:")
        for f in res:
            print(f" - {f.get('name')}")

except Exception as e:
    print(f"Error: {e}")


import httpx

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now access the variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
SUPABASE_BUCKET=os.getenv("SUPABASE_BUCKET")

# SUPABASE_PROJECT_REF = "oegqlzfdodqvgxkodynj"
# SUPABASE_URL = f"https://{SUPABASE_PROJECT_REF}.supabase.co"
# SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9lZ3FsemZkb2Rxdmd4a29keW5qIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTM2NDIyMywiZXhwIjoyMDY2OTQwMjIzfQ.bYBQ_p3g0UDfe_JL1Bb0nQCJakPMz8vM51-PKPoaQ2U"  # ⚠️ Use service_role key
# SUPABASE_BUCKET = "prescriptions"

def upload_to_supabase(file, filename):
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{filename}"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/octet-stream"
    }

    try:
       
        response = httpx.put(
            upload_url,
            content=file.read(),
            headers=headers,
            timeout=30
        )

      
        if response.status_code != 200:
            return None

        
        signed_url_api = f"{SUPABASE_URL}/storage/v1/object/sign/{SUPABASE_BUCKET}/{filename}"

        signed_headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }

        signed_response = httpx.post(
            signed_url_api,
            headers=signed_headers,
            json={"expiresIn": 31536000} 
        )

      

        if signed_response.status_code == 200:
            signed_data = signed_response.json()
            return f"{SUPABASE_URL}/storage/v1{signed_data['signedURL']}"

        return None

    except Exception as e:
        print(" Exception:", e)
        return None



 
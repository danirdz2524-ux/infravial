import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

url = Config.SUPABASE_URL
key = Config.SUPABASE_KEY

supabase = create_client(url, key)
from supabase import create_client
from utils.env_loader import get_env_var

supabase = create_client(get_env_var("SUPABASE_URL"), get_env_var("SUPABASE_KEY"))

def log_query_response(question, answer):
    try:
        supabase.table("user_logs").insert({"question": question, "answer": answer}).execute()
    except Exception as e:
        print(f"❌ Failed to log to Supabase: {e}")

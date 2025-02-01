import streamlit as st
from supabase import create_client

def get_supabase_connection():
    # Inicialização do cliente Supabase
    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )
    return supabase
import time
import os
import streamlit as st
from services import supabase_client

def load_config(supabase, user_id):
    """Load user-specific configuration from Supabase"""
    try:
        # Development logging
        if os.environ.get('STREAMLIT_ENV') == 'development':
            st.write(f"[DEBUG] Attempting to load config for user_id: {user_id}")

        # Use the public schema for Supabase tables
        response = supabase.table('user_settings').select('*').eq('user_id', user_id).execute()

        if os.environ.get('STREAMLIT_ENV') == 'development':
            st.write(f"[DEBUG] Load response: {response}")

        if response.data and len(response.data) > 0:
            return response.data[0]['settings']
        return {"text_extraction_api": "Vision API"}  # default configuration
    except Exception as e:
        st.error(f"Erro ao carregar configurações: {str(e)}")
        if os.environ.get('STREAMLIT_ENV') == 'development':
            st.write(f"[DEBUG] Detailed error while loading config: {type(e).__name__}: {str(e)}")
        return {"text_extraction_api": "Vision API"}
    
def save_config(supabase, user_id, config):
    """Save user-specific configuration to Supabase"""
    try:
        if os.environ.get('STREAMLIT_ENV') == 'development':
            st.write(f"[DEBUG] Attempting to save config for user_id: {user_id}")
            st.write(f"[DEBUG] Config to save: {config}")

        # Validate config data
        if not isinstance(config, dict):
            raise ValueError("Configuration must be a dictionary")

        # Check if a record already exists for this user
        existing_record = supabase.table('user_settings').select('*').eq('user_id', user_id).execute()

        if existing_record.data and len(existing_record.data) > 0:
            # Update existing record
            if os.environ.get('STREAMLIT_ENV') == 'development':
                st.write(f"[DEBUG] Updating existing record for user_id: {user_id}")

            response = supabase.table('user_settings')\
                .update({'settings': config})\
                .eq('user_id', user_id)\
                .execute()
        else:
            # Create new record
            if os.environ.get('STREAMLIT_ENV') == 'development':
                st.write(f"[DEBUG] Creating new record for user_id: {user_id}")

            response = supabase.table('user_settings')\
                .insert({'user_id': user_id, 'settings': config})\
                .execute()

        if os.environ.get('STREAMLIT_ENV') == 'development':
            st.write(f"[DEBUG] Save response: {response}")

        if response.data:
            return True
        return False
    except Exception as e:
        detailed_error = f"{type(e).__name__}: {str(e)}"
        st.error(f"Erro ao salvar configurações: {detailed_error}")
        if os.environ.get('STREAMLIT_ENV') == 'development':
            st.write(f"[DEBUG] Detailed error while saving config: {detailed_error}")
        return False
    
supabase = supabase_client.get_supabase_connection()
user_id = st.session_state.user.id
config = load_config(supabase, user_id)


st.title("⚙️ Configurações")

with st.form("config_form"):
    option = st.selectbox(
        "Selecione o modelo de IA a ser utilizado na extração do texto:",
        ("Vison API", "OpenAI API", "Amazon Textract", "Microsoft Azure Computer Vision"),
        index={
            "Vision API": 0,
            "OpenAI API": 1,
            "Amazon Textract": 2,
            "Microsoft Azure Computer Vision": 3
        }[config["text_extraction_api"]],
        help="Escolha qual API será utilizada para extrair texto das imagens."
    )
    btn_salvar = st.form_submit_button("Salvar")
    if btn_salvar:
        new_config = {"text_extraction_api": option}
        if save_config(supabase, user_id, new_config):
            st.success("Configurações salvas com sucesso!")
        else:
            st.error("Erro ao salvar as configurações. Por favor, tente novamente.")


import streamlit as st
import os
import services.openai_client as openai_client

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Por favor, faça login para acessar o aplicativo.")
    st.stop()

# Add custom CSS
st.markdown("""
    <style>
    .stTextArea textarea {
        font-size: 16px !important;
        min-height: 200px !important;
    }
    .evaluation-result {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Main title
st.title("📝 Avaliação de Redações")
# Add usage instructions
with st.expander("ℹ️ Como usar"):
    st.markdown("""
    1. Cole o texto da sua redação na área abaixo
    2. Clique no botão "Avaliar Redação"
    3. Aguarde a análise detalhada
    """)
st.markdown("Cole sua redação abaixo para receber uma avaliação detalhada.")

# Essay input area
essay_text = st.text_area(
    "Texto da Redação",
    height=300,
    placeholder="Cole sua redação aqui..."
)
# Evaluation button
if st.button("Avaliar Redação", type="primary", disabled=not essay_text):
    if not essay_text:
        st.error("Por favor, insira uma redação para avaliar.")
    else:
        try:
            with st.spinner("Analisando sua redação... Por favor, aguarde."):
                evaluation = openai_client.evaluate_essay(essay_text)
            st.info("Resultado da Avaliação")
            st.markdown('<div class="evaluation-result">', unsafe_allow_html=True)
            st.markdown(evaluation)
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Ocorreu um erro: {str(e)}")
            if "api_key" in str(e).lower():
                st.warning("Por favor, verifique se sua chave de API da OpenAI está configurada corretamente.")
            elif "assistant" in str(e).lower():
                st.warning("Por favor, verifique se o ID do assistente OpenAI está configurado corretamente.")
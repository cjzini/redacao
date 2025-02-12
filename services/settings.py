import time
import streamlit as st


st.write("## Configurações")

with st.form("config_form"):
    option = st.selectbox(
        "Selecione o modelo de IA a ser utilizado na extração do texto:",
        ("Google Vison API", "Amazon Textract", "Microsoft Azure Computer Vision"),
    )
    btn_salvar = st.form_submit_button("Salvar")
    if btn_salvar:
        st.success("AI selecionada: {}".format(option))
        time.sleep(2)
        st.rerun()
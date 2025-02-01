import time
import streamlit as st

st.write("## Configurações")

with st.form("config_form"):
        pasta = st.text_input('Diretório de trabalho', value='D:\\Temp\\XML')
        btn_salvar = st.form_submit_button("Salvar")
        if btn_salvar:
            st.success("Configurações salvas com sucesso!")
            time.sleep(2)
            st.rerun()
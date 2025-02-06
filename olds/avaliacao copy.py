import streamlit as st
import pytesseract
from PIL import Image
import io

st.header('Avaliação de Redação')
st.write('Faça o upload de uma imagem contendo texto manuscrito para convertê-lo em texto digital.')

# Widget para upload de imagem
uploaded_file = st.file_uploader("Escolha uma imagem da redação manuscrito", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # Exibir a imagem carregada
    image = Image.open(uploaded_file)
    st.image(image, caption='Imagem carregada', use_column_width=True)
    
    # Botão para iniciar a extração de texto
    if st.button('Extrair Texto'):
        try:
            # Realizar OCR na imagem
            texto_extraido = pytesseract.image_to_string(image, lang='por')
            
            # Exibir o texto extraído
            st.subheader('Texto Extraído:')
            st.write(texto_extraido)
            
            # Opção para baixar o texto extraído
            st.download_button(
                label="Baixar texto extraído",
                data=texto_extraido,
                file_name="texto_extraido.txt",
                mime="text/plain"
            )
        except Exception as e:
            st.error(f'Erro ao processar a imagem: {str(e)}')
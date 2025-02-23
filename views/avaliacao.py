import streamlit as st
from PIL import Image
from views.utils import process_image, exibir_texto

st.title("✍️ Conversão de Texto Manuscrito")
st.markdown("""
    Faça o upload de uma imagem de uma redação contendo texto manuscrito para convertê-lo em texto digital.
    """)

# Widget para upload de imagem
uploaded_file = st.file_uploader("Escolha um arquivo de imagem", 
                                 type=['png', 'jpg', 'jpeg'],
                                 help="Selecione uma imagem da redação manuscrita para extração do texto.")

if uploaded_file is not None:
    # Exibir a imagem carregada
    image = Image.open(uploaded_file)
    st.image(image, caption='Imagem carregada', use_container_width=True)
    
    # Botão para iniciar a extração de texto
    if st.button('Extrair Texto'):
        try:
            with st.spinner('Processando imagem...'):
                # Realizar OCR na imagem
                texto_extraido = process_image(uploaded_file.getvalue())
                #texto_analise = exibir_texto(uploaded_file.getvalue())
                
                # Exibir o texto extraído
                # st.subheader('Texto Extraído:')
                # st.text(texto_extraido)

                txt = st.text_area("Texto Extraído", texto_extraido, height=800)
                
                # Opção para baixar o texto extraído
                st.download_button(
                    label="Baixar texto extraído",
                    data=texto_extraido,
                    file_name="texto_extraido.txt",
                    mime="text/plain"
                )

                #st.subheader('Analise:')
                #st.markdown(texto_analise)

        except Exception as e:
            st.error(f'Erro ao processar a imagem: {str(e)}')
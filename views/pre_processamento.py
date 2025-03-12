import streamlit as st
import io
from PIL import Image
import services.image_preprocess as image_preprocess
import services.visionai_client as visionai_client
import services.openai_client as openai_client

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Por favor, faça login para acessar o aplicativo.")
    st.stop()

st.title("✍️ Extração de Texto Manuscrito")
st.markdown("""
Faça o upload de uma imagem de uma redação contendo texto manuscrito para transcreve-lo em texto digital.
""")
# supabase = supabase_client.get_supabase_connection()
# user_id = st.session_state.user.id
# ia_selected = settings.load_config(supabase, user_id)["text_extraction_api"]
# API Selection
api_option = st.selectbox(
    "Selecionar API para extração de texto",
    options=["Vision API", "OpenAI API"],
    help="Escolha qual API será utilizada para extrair texto das imagens"
)
st.info(f"AI selecionada: **{api_option}**")

# Add usage instructions
with st.expander("ℹ️ Como usar"):
    st.markdown("""
    1. Clique no botão 'Escolher Arquivo' abaixo
    2. Selecione uma imagem contendo texto manuscrito.
    3. Clique no botão 'Extrair Texto'
    4. Aguarde o processamento da imagem
    5. Visualize o texto extraído
    6. Se desejar, clique no botão 'Baixar texto extraído'
                
    Formatos de imagem suportados: PNG, JPG, JPEG
    """)

# Add image preprocessing options
st.subheader("Opções de Pré-processamento")

col1, col2 = st.columns(2)

with col1:
    use_grayscale = st.checkbox("Aplicar escala de cinza", value=True)
    use_threshold = st.checkbox("Aplicar binarização", value=True,
                                help="Para esse filtro funcionar, é obrigatório aplicar a escala de cinza")
    use_denoising = st.checkbox("Aplicar redução de ruído", value=True)

with col2:
    use_contrast = st.checkbox("Aumentar contraste (CLAHE)", value=False)
    use_morphological = st.checkbox("Aplicar dilatação e erosão", value=False,
                                    help="Ajuda a reforçar os contornos das letras")

# File uploader
uploaded_file = st.file_uploader(
    "Escolha um arquivo de imagem", 
    type=["png", "jpg", "jpeg"],
    help="Selecione uma imagem da redação manuscrita para extração do texto."
)
st.html(
        """
        <style>

        [data-testid='stFileUploaderDropzoneInstructions'] > div > span {
        display: none;
        }

        [data-testid='stFileUploaderDropzoneInstructions'] > div::before {
        content: 'Arraste e solte o arquivo aqui';
        }


        [data-testid='stFileDropzoneInstructions'] { text-indent: -9999px; line-height: 0; } [
        
        data-testid='stFileDropzoneInstructions']::after { line-height: initial; 
        content: "Limite 200MB por arquivo"; text-indent: 0; }
    }
        </style>
        """
    )

if uploaded_file is not None:
    try:
        # Get the original image
        image_bytes = uploaded_file.getvalue()
        original_image = Image.open(uploaded_file)

        # Get the preprocessed image with selected filters
        processed_bytes = image_preprocess.preprocess_image(
            image_bytes,
            use_grayscale=use_grayscale,
            use_threshold=use_threshold,
            use_denoising=use_denoising,
            use_contrast_enhancement=use_contrast,
            use_morphological=use_morphological
        )
        processed_image = Image.open(io.BytesIO(processed_bytes))

        # Display both images side by side
        st.subheader("Comparação de Imagens")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Imagem Original:")
            st.image(original_image, use_container_width=True)
        with col2:
            st.write("Imagem Pré-processada:")
            st.image(processed_image, use_container_width=True)

        # Add option to choose which image to process
        image_choice = st.radio(
            "Selecione a imagem para extrair o texto:",
            ("Imagem Pré-processada","Imagem Original")
        )

        # Add process button
        if st.button("Extrair Texto"):
            with st.spinner('Processando imagem...'):
                # Select which image to process
                img_to_process = image_bytes if image_choice == "Imagem Original" else processed_bytes

                # Process the image using selected API
                if api_option == 'Vision API':
                    extracted_text = visionai_client.process_image(img_to_process)
                else:  # Default to OpenAI API
                    extracted_text = openai_client.process_image(img_to_process)

            # Display results
            st.text_area("Texto Extraído", extracted_text, height=800)

            # Add download button for extracted text
            st.download_button(
                label="Baixar texto extraído",
                data=extracted_text,
                file_name="texto_extraido.txt",
                mime="text/plain"
            )

    except Exception as e:
        st.error(f"Erro ao processar a imagem: {str(e)}")
        st.error("Certifique-se que você tenha selecionado uma imagem válida.")
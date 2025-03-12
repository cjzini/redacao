from http import client
import streamlit as st
import base64
from openai import OpenAI
from openai import OpenAIError

def get_openai_client():
    """Initialize OpenAI client"""
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    if not openai_api_key:
        raise Exception("OpenAI API key not found in environment variables")
    return OpenAI(api_key=openai_api_key)

def process_image(image_content):
    """
    Extract text from image using OpenAI's Vision model
    """
    try:
        client = get_openai_client()
        
        # Convert image bytes to base64
        base64_image = base64.b64encode(image_content).decode('utf-8')
        
        # Call OpenAI API with vision model
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "This is an image of a handwritten essay in Brazilian Portuguese. "
                                    "Note that there are some digital characters in the image, but extract only the handwritten text from this image, trying to be as accurate as possible. "
                                    "Do not alter the text by making any interpretations. "
                                    "Just extract the handwritten text. "
                                    "The answer should be only the extracted text in a clear and legible format."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        # Extract the text from response
        extracted_text = response.choices[0].message.content
        
        if not extracted_text or extracted_text.strip() == "":
            return "Nenhum texto manuscrito detectado na imagem."
            
        return extracted_text
        
    except Exception as e:
        raise Exception(f"Erro ao processar imagem com OpenAI: {str(e)}")

def evaluate_essay(essay_text):
    """
    Send the essay text to a specific OpenAI Assistant for evaluation
    """
    try:
        client = get_openai_client()
        # Acessa diretamente o Assitente pré-criado na OpenAI
        ASSISTANT_ID = st.secrets["OPENAI_ASSISTANT_ID"]
        if not ASSISTANT_ID:
            raise Exception("O ID do Assistente da OpenAI não está configurado.")

        # Create a thread
        thread = client.beta.threads.create()

        # Add message to thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=essay_text
        )

        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Wait for the run to complete
        while run.status not in ["completed", "failed"]:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

        if run.status == "failed":
            raise Exception("Assistente de IA falhou em processar a redação. Por favor, tente novamente.")

        # Get the assistant's response
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )

        # Return the latest assistant message
        return messages.data[0].content[0].text.value

    except OpenAIError as e:
        raise Exception(f"Erro ao communicar com a OpenAI API: {str(e)}")
    except Exception as e:
        raise Exception(f"Um erro inesperado ocorreu: {str(e)}")
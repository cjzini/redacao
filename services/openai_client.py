import streamlit as st
import base64
from openai import OpenAI

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
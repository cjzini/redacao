import json
import os
from google.cloud import vision
from google.oauth2 import service_account
import io

def get_vision_client():
    """
    Create and return an authenticated Vision API client
    """
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'util/palavra-mestra.json'
        # Return authenticated client
        return vision.ImageAnnotatorClient()
    except Exception as e:
        raise Exception(f"Falha ao inicializar o cliente Vision: {str(e)}")

def process_image(image_content):
    """
    Process the image using Google Cloud Vision API and extract text.

    Args:
        image_content (bytes): The image content in bytes

    Returns:
        str: Extracted text from the image
    """
    try:
        # Get authenticated client
        client = get_vision_client()

        # Create image object
        image = vision.Image(content=image_content)

        # Configure image context with language hints
        image_context = vision.ImageContext(
            language_hints=['pt-BR']  # Set Portuguese (Brazil) as primary language
        )

        # Perform handwritten text detection with language hints
        response = client.text_detection(
            image=image,
            image_context=image_context
        )
        # Get full text annotations
        #document = response.full_text_annotation
        document = response.full_text_annotation

        if response.error.message:
            raise Exception(
                f'{response.error.message}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors')

        # Extract only handwritten text based on confidence scores
        handwritten_text = []
        for page in document.pages:
            for block in page.blocks:
                # Handwritten text typically has lower confidence scores
                # We'll consider text with confidence < 0.9 as handwritten
                if block.confidence < 0.9:
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:
                            word_text = ''.join([
                                symbol.text for symbol in word.symbols
                            ])
                            handwritten_text.append(word_text)

        if not handwritten_text:
            return "Não foi detectado texto escrito a mão na imagem."

        # Join all handwritten words with spaces
        return ' '.join(handwritten_text)

    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")
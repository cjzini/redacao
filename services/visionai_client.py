
import streamlit as st 
from google.cloud import vision
import os
import re

def get_vision_client():
    """
    Create and return an authenticated Vision API client
    """
    try:
        #os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'util/palavra-mestra.json'
        # Streamlit Cloud Deploy:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = st.secrets["visionapi"]['palavra-mestra']
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
        response = client.document_text_detection(
            image=image,
            image_context=image_context
        )
        # Get full text annotations
        document = response.full_text_annotation

        if response.error.message:
            raise Exception(
                f'{response.error.message}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors')

        # Extract only handwritten text based on confidence scores
        paragraphs = []

        for page in document.pages:
            for block in page.blocks:
                # Handwritten text typically has lower confidence scores
                # We'll consider text with confidence < 0.5 as handwritten
                # since printed text usually has very high confidence (>0.9)
                #if block.confidence < 0.98:
                    # Process each paragraph separately
                for paragraph in block.paragraphs:
                    paragraph_text = []
                    for word in paragraph.words:
                        word_text = ''.join([
                            symbol.text for symbol in word.symbols
                        ])
                        paragraph_text.append(word_text)

                    if paragraph_text:
                        # Clean the formatting of each paragraph separately
                        clean_paragraph = clean_text_formatting(' '.join(paragraph_text))
                        paragraphs.append(clean_paragraph)

        if not paragraphs:
            return "No handwritten text detected in the image."

        # Join paragraphs with double newlines to create clear separation
        return '\n'.join(paragraphs)

    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

def clean_text_formatting(text):
    """
    Clean the text formatting by removing spaces before punctuation
    and normalizing other spacing issues.
    """
    # Remove spaces before punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    # Remove spaces around quotes and hyphens
    text = re.sub(r'\s*"\s*', '"', text)  # Remove spaces around quotes
    text = re.sub(r'\s*-\s*', '-', text)  # Remove spaces around hyphens
    # Normalize spaces between words
    text = ' '.join(text.split())
    return text
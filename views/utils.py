import json
import os
from google.cloud import vision
import re
import cv2
import numpy as np

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
    
def preprocess_image(image_bytes, use_grayscale=True, use_threshold=True, use_denoising=True):
    """
    Preprocess the image using OpenCV to improve OCR accuracy.

    Args:
        image_bytes (bytes): Raw image bytes
        use_grayscale (bool): Whether to apply grayscale conversion
        use_threshold (bool): Whether to apply adaptive thresholding
        use_denoising (bool): Whether to apply denoising

    Returns:
        bytes: Processed image bytes ready for OCR
    """
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Apply selected preprocessing steps
    if use_grayscale:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if use_threshold and use_grayscale:  # Thresholding requires grayscale image
        img = cv2.adaptiveThreshold(
            img, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 
            2
        )

    if use_denoising:
        if use_grayscale:
            img = cv2.fastNlMeansDenoising(img)
        else:
            img = cv2.fastNlMeansDenoisingColored(img)

    # Convert back to bytes
    success, processed_image = cv2.imencode('.png', img)
    if not success:
        raise Exception("Failed to encode processed image")

    return processed_image.tobytes()

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

def exibir_texto(image_content):
    markdown = ""
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
        
        for page in document.pages:
            for block in page.blocks:
                markdown += f"\n\nBlock confidence: {block.confidence}\n"
                markdown += "\n"

                for paragraph in block.paragraphs:
                    markdown += f"Paragraph confidence: {paragraph.confidence}\n"
                    markdown += "\n"

                    for word in paragraph.words:
                        word_text = "".join([symbol.text for symbol in word.symbols])
                        markdown += f"Word text: {word_text} (confidence: {word.confidence})\n"
                        markdown += "\n"

                        # for symbol in word.symbols:
                        #     markdown += f"\tSymbol: {symbol.text} (confidence: {symbol.confidence})\n"
                    markdown += '\n'

        return markdown
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

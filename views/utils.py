import json
import os
from google.cloud import vision
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
        
        #testes_imagem(response)

        # Join all handwritten words with spaces
        return ' '.join(handwritten_text)

    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")
    
def testes_imagem(response):
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            print(f"\nBlock confidence: {block.confidence}\n")

            for paragraph in block.paragraphs:
                print("Paragraph confidence: {}".format(paragraph.confidence))

                for word in paragraph.words:
                    word_text = "".join([symbol.text for symbol in word.symbols])
                    print(
                        "Word text: {} (confidence: {})".format(
                            word_text, word.confidence
                        )
                    )

                    for symbol in word.symbols:
                        print(
                            "\tSymbol: {} (confidence: {})".format(
                                symbol.text, symbol.confidence
                            )
                        )
def exibir_texto(response):
    markdown = ""

    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            markdown += f"\nBlock confidence: {block.confidence}\n"

            for paragraph in block.paragraphs:
                markdown += f"Paragraph confidence: {paragraph.confidence}\n"

                for word in paragraph.words:
                    word_text = "".join([symbol.text for symbol in word.symbols])
                    markdown += f"Word text: {word_text} (confidence: {word.confidence})\n"

                    for symbol in word.symbols:
                        markdown += f"\tSymbol: {symbol.text} (confidence: {symbol.confidence})\n"

    return markdown

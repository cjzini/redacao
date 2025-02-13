import cv2
import numpy as np

def preprocess_image(image_bytes, use_grayscale=True, use_threshold=True, use_denoising=True, use_contrast_enhancement=False, use_morphological=False):
    """
    Preprocess the image using OpenCV to improve OCR accuracy.

    Args:
        image_bytes (bytes): Raw image bytes
        use_grayscale (bool): Whether to apply grayscale conversion
        use_threshold (bool): Whether to apply adaptive thresholding
        use_denoising (bool): Whether to apply denoising
        use_contrast_enhancement (bool): Whether to apply CLAHE for contrast enhancement
        use_morphological (bool): Whether to apply morphological operations (dilation and erosion)

    Returns:
        bytes: Processed image bytes ready for OCR
    """
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Apply selected preprocessing steps
    if use_grayscale:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if use_contrast_enhancement:
        if use_grayscale:
            # Apply CLAHE to grayscale image
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            img = clahe.apply(img)
        else:
            # For color images, apply CLAHE to L channel in LAB color space
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            lab = cv2.merge((l,a,b))
            img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    if use_threshold and use_grayscale:  # Thresholding requires grayscale image
        img = cv2.adaptiveThreshold(
            img, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 
            2
        )

    if use_morphological and use_grayscale:
        # Define kernel size for morphological operations
        kernel = np.ones((2,2), np.uint8)
        # Apply dilation followed by erosion to enhance text contours
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)

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
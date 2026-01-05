import cv2
import numpy as np
from PIL import Image


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Nettoie l'image pour améliorer l'OCR
    """
    # Conversion PIL → OpenCV
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Passage en niveaux de gris
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Réduction du bruit
    gray = cv2.medianBlur(gray, 3)

    # Binarisation
    _, thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return Image.fromarray(thresh)
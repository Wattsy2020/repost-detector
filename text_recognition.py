import pytesseract
import cv2
from PIL import Image
import os
import re
import autocorrect

common_words = ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with',
                'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
                'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there',
                'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who',
                'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like',
                'time', 'no', 'just', 'him', 'know', 'take', 'people', 'into',
                'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
                'than', 'now', 'look', 'only', 'come', 'its', 'over', 'think',
                'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
                'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any'
                'these', 'give', 'day', 'most', 'us']


def parse_ocr_text(words):
    corrected_words = []

    for word in words:
        if len(word) < 15:  # ignore long words as they are likely OCR inaccuracies
            word = autocorrect.spell(word)  # correct spelling errors
            corrected_words.append(word)

    return corrected_words


def remove_common_words(words):
    keywords = []

    for word in words:
        if word not in common_words:
            keywords.append(word)
    return keywords


def get_words(text):
    if not text: return [""]

    text = text.strip().lower()  # remove whitespace and transform to lowercase
    text = re.sub('[^a-zA-Z0-9\s]+', '', text)  # remove non alphanumeric characters
    keywords = text.split(' ')  # split into a list of words

    return keywords


def get_image_text(image_path):
    if image_path == '': return
    image = cv2.imread(image_path, 0)

    # modify the image to make tesseract more effective
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    image = cv2.medianBlur(image, 3)

    # save and load the modified image
    filename = '{}-ocr.png'.format(image_path)
    cv2.imwrite(filename, image)
    modified_image = Image.open(filename)

    # use tesseract to get text from image
    text = pytesseract.image_to_string(modified_image).encode('utf-8')

    # remove modified image to save space
    os.remove(filename)
    return str(text)

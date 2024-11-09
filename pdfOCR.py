import pdfplumber
import pytesseract
from PIL import Image

# Set the path to the tesseract executable if needed (for Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_pdf_with_ocr(pdf_path):
    text_content = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
           # if page.extract_text():  # If text is available, extract it
            #    text_content += page.extract_text()
            #else:
                # Perform OCR with Arabic language on image-based pages
                page_image = page.to_image(resolution=300)
                pil_image = page_image.original  # Get the PIL Image
                ocr_text = pytesseract.image_to_string(pil_image, lang="ara")  # Specify Arabic language
                text_content += ocr_text
    return text_content

pdf_path = r"C:\Users..."
extracted_text = extract_text_from_pdf_with_ocr(pdf_path)

print(extracted_text)

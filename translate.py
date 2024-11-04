import re
from google_trans_new import google_translator
from deep_translator import GoogleTranslator
import PyPDF2
from docx import Document

# Initialize the translator
translator = google_translator()

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# Function to extract text from Word
def extract_text_from_word(docx_path):
    doc = Document(docx_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

# Function to split text into chunks for translation
def split_text(text, max_length=5000):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    chunks.append(current_chunk.strip())  # Add last chunk
    return chunks

# Function to translate text chunk by chunk
def translate_long_text(text, src_lang='tr', dest_lang='en'):
    chunks = split_text(text)
    translated_chunks = [translator.translate(chunk, src=src_lang, dest=dest_lang).text for chunk in chunks]
    return ' '.join(translated_chunks)

def translate_text(text, src_lang='tr', dest_lang='en'):
    tt = GoogleTranslator(source=src_lang, target=dest_lang).translate(text)
    return tt

# Main function to handle the full process
def translate_document(input_file, file_type):
    if file_type == 'pdf':
        original_text = extract_text_from_pdf(input_file)
    elif file_type == 'word':
        original_text = extract_text_from_word(input_file)
    else:
        raise ValueError("Unsupported file type. Use 'pdf' or 'word'.")

    print("Translating from Turkish to English...")
    translated_text = translate_long_text(original_text, src_lang='tr', dest_lang='en')

    # Instead of saving the translated text, print it directly
    print("Translated Text:\n")
    print(translated_text)

# Example usage:
if __name__ == "__main__":
    # Specify your input file path
    input_file = "test_document.docx"  # or "input_document.docx"
    file_type = "word"  # Set 'pdf' or 'word' based on the input file type

    translate_document(input_file, file_type)

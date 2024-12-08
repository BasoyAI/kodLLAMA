import re
import translate
from PyPDF2 import PdfReader
from docx import Document

def read_text_from_file(uploaded_file):
    file_type = uploaded_file.name.split(".")[-1].lower()
    
    if file_type == "pdf":
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    
    elif file_type == "docx":
        doc = Document(uploaded_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    
    elif file_type == "txt":
        text = str(uploaded_file.read(), "utf-8")
        return text
    
    else:
        return "Unsupported file type"

def split_into_sentences(text):

    sentences = re.split(r'(?<=[.!?]) +', text.strip())
    final_sentences = []
    for i, sentence in enumerate(sentences):
        translated_text = translate.translate_text(sentence, "tr", "en")
        final_sentences.append({"id":i, "start": None, "end": None, "text": sentence,
                                            "translated_text": translated_text})

    return final_sentences

import json

from ollama import chat
import re
from PyPDF2 import PdfReader
from docx import Document
import transcript
import tempfile
from difflib import get_close_matches


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
    return sentences

def generate_subheading(text, promptText, heading, headings):
    messages = [
        {
            'role': 'user',
            'content': (
                "You are a bot that analyzes texts. Your task is to generate suitable subtitle for the provided text. "
                "You need to analyze the text and create the most appropriate subtitle. "
                "Each title should be no more than five words. Please provide only the subtite as output. "
                "Do not add number to subtitle or add any comments. "
                f"You can not create the same with any of these titles: {", ".join(headings)}."
                f"You must create a relative subtitle with the main title and text. The main title is: '{heading}'"
                f"The topic of the provided text and your task is as follows: '{promptText}', and the text is as follows: '{text}'."
            )
        },
    ]

    response = chat('llama3.2', messages=messages)
    created_subtitle = response['message']['content'].strip()
    headings[heading].append(created_subtitle)
    return created_subtitle

def generate_headings(text, promptText):
    messages = [
        {
            'role': 'user',
            'content': (
                "You are a bot that analyzes texts. Your task is to generate suitable titles for the provided text. "
                "You need to analyze the text and create the most appropriate titles. Do not generate any subtitles. "
                "Each title should be no more than five words. Please provide only the titles as output. "
                "Do not number them or add any comments. "
                f"The topic of the provided text and your task is as follows: '{promptText}', and the text is as follows: '{text}'."
            )
        },
    ]
    
    response = chat('llama3.2', messages=messages)
    headings = response['message']['content'].strip().split("\n")
    headings = [heading.strip() for heading in headings if heading.strip()]

    # Sözlük oluşturma
    cleaned_headings = {}
    for heading in headings:
        # Eğer başlık numaralı ise numarayı kaldır
        if len(heading) >= 3 and heading[0].isdigit() and heading[1] == '.' and heading[2] == ' ':
            heading_name = heading[3:]
        else:
            heading_name = heading
        
        # Dictionary'e başlık ve boş bir liste ekle
        cleaned_headings[heading_name] = []

    return cleaned_headings


def categorize_sentences_audio(sentences, headings):
    categorized_dict = {title: [] for title in headings}
    categorized_dict["none"] = []

    for sentence in sentences:
        messages = [
            {
                'role': 'user',
                #'role': 'system',
                'content': f'Choose one heading that this sentence fits. Your response must be only the heading that you choose. Do not make any comments or write other characters. Sentence: "{sentence["translated_text"]}" Headings: {", ".join(headings)}'
            },
        ]
        response = chat('llama3.2', messages=messages)
        chosen_title = response['message']['content'].strip()

        if chosen_title in headings:
            sentence["heading"] = chosen_title
        else:
            sentence["heading"] = "None"
            print(f"Error: Heading '{chosen_title}' not found. Could not categorize sentence: '{sentence['translated_text']}'")

    return sentences

from difflib import get_close_matches

def categorize_sentences(sentences, headings):
    # headings sözlüğündeki anahtarları alıyoruz
    heading_keys = list(headings.keys())

    # Başlıkları boş bir listeyle başlatıyoruz
    categorized_dict = {title: [] for title in heading_keys}
    categorized_dict["none"] = []
    
    print(heading_keys)
    
    for sentence in sentences:
        messages = [
            {
                'role': 'user',
                'content': f'Choose one heading that this sentence fits. Your response must be only the heading that you choose. Do not make any comments or write other characters. Sentence: "{sentence}" Headings: {", ".join(heading_keys)}'
            },
        ]
        response = chat('llama3.2', messages=messages)
        chosen_title = response['message']['content'].strip()
        
        # En yakın eşleşen başlığı bul
        closest_match = get_close_matches(chosen_title, heading_keys, n=1, cutoff=0.6)
        
        if closest_match:
            # En yakın eşleşme bulunduysa bunu kullan
            matched_heading = closest_match[0]
            categorized_dict[matched_heading].append(sentence)
        else:
            # Eğer eşleşme bulunmazsa "none" kategorisine ekle
            categorized_dict["none"].append(f"Chosen Title: {chosen_title}, sentence: {sentence}")
            print(f"Error: Heading '{chosen_title}' not found. Could not categorize sentence: '{sentence}'")

    return categorized_dict


def process_text(uploaded_file, promptText):
    # Dosyadan metni okuma
    if uploaded_file.type == ("audio/mpeg" or "video/mp4"):
        temp_file_path = ""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        sentences = transcript.process_file(temp_file_path)

        text = ""
        for sentence in sentences:
            text += sentence["translated_text"] + " "

        headings = generate_headings(text, promptText)
        updated_sentences = categorize_sentences_audio(sentences, headings)

        result = {
            "categorized_dict": updated_sentences,
            "sentences": sentences,
            "raw_text": text,  # Ham metni kaydetme
            "headings": headings,
            "type": "audio"
        }

        print(json.dumps(result, ensure_ascii=False, indent=4))
        return result
    else:
        text = read_text_from_file(uploaded_file)

        # Cümlelere ayırma ve başlık oluşturma
        sentences = split_into_sentences(text)
        headings = generate_headings(text, promptText)
        categorized_dict = categorize_sentences(sentences, headings)

        return {
            "categorized_dict": categorized_dict,
            "sentences": sentences,
            "raw_text": text,  # Ham metni kaydetme
            "headings": headings,
            "type": "text_file"
        }
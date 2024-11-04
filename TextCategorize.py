import json

from ollama import chat
import re
from PyPDF2 import PdfReader
from docx import Document
import transcript
import tempfile

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

def generate_headings(text):
    messages = [
        {
            'role': 'user',
            #'role': 'system',
            'content': f'You are a bot that analyzes customer complaints. Your task is to categorize the complaints into headings. Review the text and generate appropriate headings based on the content. Do not create subheadings. Headings should be a maximum of 5 words. Provide only the headings as feedback. Do not order them by numbers. The content is: "{text}"'
        },
    ]
    
    response = chat('llama3.2', messages=messages)
    headings = response['message']['content'].strip().split("\n")
    headings = [heading.strip() for heading in headings if heading.strip()]

    cleaned_headings = []
    for heading in headings:
        if len(heading) >= 3 and heading[0].isdigit() and heading[1] == '.' and heading[2] == ' ':
            cleaned_headings.append(heading[3:])
        else:
            cleaned_headings.append(heading)
    
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

def categorize_sentences(sentences, headings):
    categorized_dict = {title: [] for title in headings}
    categorized_dict["none"] = []
    for sentence in sentences:
        messages = [
            {
                'role': 'user',
                #'role': 'system',
                'content': f'Choose one heading that this sentence fits. Your response must be only the heading that you choose. Do not make any comments or write other characters. Sentence: "{sentence}" Headings: {", ".join(headings)}'
            },
        ]
        response = chat('llama3.2', messages=messages)
        chosen_title = response['message']['content'].strip()

        if chosen_title in categorized_dict:
            categorized_dict[chosen_title].append(sentence)
        else:
            categorized_dict["none"].append("Choosen Title: " + chosen_title + ", sentence: " + sentence)
            print(f"Error: Heading '{chosen_title}' not found. Could not categorize sentence: '{sentence}'")

    return categorized_dict

def process_text(uploaded_file):
    # Dosyadan metni okuma
    if uploaded_file.type == "audio/mpeg" or "video/mp4":
        temp_file_path = ""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        sentences = transcript.process_file(temp_file_path)

        text = ""
        for sentence in sentences:
            text += sentence["translated_text"] + " "

        headings = generate_headings(text)
        updated_sentences = categorize_sentences_audio(sentences, headings)

        result = {
            "categorized_dict": updated_sentences,
            "sentences": sentences,
            "raw_text": text  # Ham metni kaydetme
        }

        print(json.dumps(result, ensure_ascii=False, indent=4))
        return result
    else:
        text = read_text_from_file(uploaded_file)

        # Cümlelere ayırma ve başlık oluşturma
        sentences = split_into_sentences(text)
        headings = generate_headings(text)
        categorized_dict = categorize_sentences(sentences, headings)

        return {
            "categorized_dict": categorized_dict,
            "sentences": sentences,
            "raw_text": text  # Ham metni kaydetme
        }
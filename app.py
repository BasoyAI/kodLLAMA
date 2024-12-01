from ai import categorize_sentences, generate_subheading, generate_headings
import json
import transcript
import tempfile
import process_text

prompt = ""
uploaded_file = None
headings = None
processed_out = None


def generate_subheading_(parent_heading_index):
    new_subheading_code = headingSystems(parent_heading_index)
    parent_heading_value = headings[parent_heading_index]
    new_subheading_value = generate_subheading(headingSystems.get_sentences_only_at(parent_heading_code).join, prompt, parent_heading_value, headings)
    
    headings[new_subheading_code] = new_subheading_value
    headings_buffer = headings = {
        0: parent_heading_value,
        1: new_subheading_value,
    }

    only_parent_heading_texts = headingSystems.get_sentences_at_only(parent_heading_code)
    categorize_sentences(only_parent_heading_texts, headings_buffer)


#process_file_ai buraya taşı
def process_file(uploaded_file_, prompt_text):
    prompt = prompt_text
    uploaded_file = uploaded_file_

    if uploaded_file.type == ("audio/mpeg" or "video/mp4"):
        temp_file_path = ""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        sentences = transcript.process_file(temp_file_path)

        text = ""
        for sentence in sentences:
            text += sentence["translated_text"] + " "

        headings = generate_headings(text, prompt)
        updated_sentences = categorize_sentences(sentences, headings)

        processed_out = {
            "categorized_dict": updated_sentences,
            "sentences": sentences,
            "raw_translated_text": text,  # Ham metni kaydetme
            "headings": headings,
            "type": "audio"
        }

        print(json.dumps(processed_out, ensure_ascii=False, indent=4))
    else:
        text = process_text.read_text_from_file(uploaded_file)

        # Cümlelere ayırma ve başlık oluşturma
        sentences = process_text.split_into_sentences(text)
        headings = generate_headings(text, prompt)
        categorized_dict = categorize_sentences(sentences, headings)

        processed_out = {
            "categorized_dict": categorized_dict,
            "sentences": sentences,
            "raw_translated_text": text,  # Ham metni kaydetme
            "headings": headings,
            "type": "text_file"
        }



    print("Kategorize Sonuçları")
    print("-----------------------")
    print(json.dump(processed_out))
    '''
    print(processed_out["categorized_dict"])
    print("-----------------------")
    print(processed_out["sentences"]) 
    print("-----------------------")
    print(processed_out["headings"]) 
    print("-----------------------")
    print(processed_out["type"]) 
    print("-----------------------")
    print(processed_out["raw_translated_text"]) 
    '''

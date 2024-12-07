from ai import categorize_sentences, generate_subheading, generate_headings
import json
import transcript
import tempfile
import process_text
import heading_system

prompt = ""
uploaded_file = None
headings = None
processed_out = {
            "categorized_dict": {},
            "sentences": [],
            "raw_translated_text": "", 
            "headings": {},
            "type": ""
        }

def generate_subheading_(parent_heading_index, subheading_prompt):
    global processed_out
    global prompt
    global headings
    new_subheading_index = heading_system.generate_heading_index(headings,parent_heading_index)
    parent_heading_value = headings[parent_heading_index]
    sub_prompt = ""
    if subheading_prompt is not None or subheading_prompt == "":
        sub_prompt = subheading_prompt
    else:
        sub_prompt = prompt 
    new_subheading_value = generate_subheading(heading_system.find_sentences(processed_out["sentences"], parent_heading_index), sub_prompt, parent_heading_value, headings)
    
    headings[new_subheading_index] = new_subheading_value
    headings_buffer = {
        parent_heading_index: parent_heading_value,
        new_subheading_index: new_subheading_value,
    }
    only_parent_heading_texts = heading_system.find_sentences_as_objects(processed_out["sentences"], parent_heading_index)
    sentences_buffer = []
    sentences_buffer = categorize_sentences(only_parent_heading_texts, headings_buffer)
    processed_out["sentences"] = heading_system.change_sentence_headings(processed_out["sentences"], sentences_buffer)
    headings = heading_system.sort_headings(headings)
    print(json.dumps(processed_out, ensure_ascii=False, indent=4))

    #rerun front-end

#process_file_ai buraya taşı
def process_file(uploaded_file_, prompt_text):
    global processed_out
    global prompt
    global headings
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
            "sentences": updated_sentences,
            "raw_translated_text": text,  # Ham metni kaydetme
            "headings": headings,
            "type": "audio"
        }

        print(json.dumps(processed_out, ensure_ascii=False, indent=4))
    else:
        text = process_text.read_text_from_file(uploaded_file)

        # Cümlelere ayırma ve başlık oluşturma
        sentences = process_text.split_into_sentences(text)

        text = ""
        for sentence in sentences:
            text += sentence["translated_text"] + " "
        headings = generate_headings(text, prompt)
        categorized_dict = categorize_sentences(sentences, headings)

        processed_out = {
            "categorized_dict": categorized_dict,
            "sentences": sentences,
            "raw_translated_text": text,  # Ham metni kaydetme
            "headings": headings,
            "type": "text_file"
        }
    headings = heading_system.sort_headings(headings)


    print("Kategorize Sonuçları")
    print("-----------------------")
    print(json.dumps(processed_out, ensure_ascii=False, indent=4))
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

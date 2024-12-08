from ai import categorize_sentences, generate_subheading, generate_headings
import transcript
import tempfile
import process_text
import heading_system

def generate_subheading_(parent_heading_index, subheading_prompt, processed_out, headings, prompt_text):
    # Yeni alt başlık index'i oluştur
    new_subheading_index = heading_system.generate_heading_index(headings, parent_heading_index)
    parent_heading_value = headings.get(parent_heading_index, "Unknown Heading")

    # Eğer subheading promptu girilmediyse, genel prompt'u kullan
    sub_prompt = subheading_prompt if subheading_prompt else prompt_text

    # Yeni alt başlık metnini üret
    new_subheading_value = generate_subheading(
        heading_system.find_sentences(processed_out["sentences"], parent_heading_index),
        sub_prompt,
        parent_heading_value,
        headings
    )

    # Yeni alt başlığı headings'e ekle
    headings[new_subheading_index] = new_subheading_value
    headings = heading_system.sort_headings(headings)

    # Bu noktada yeni bir alt başlık oluştu. Bu alt başlık, parent heading altında bulunan bazı cümleler için daha uygun olabilir.
    # Bu nedenle sadece parent heading altındaki cümleleri tekrar kategorize edeceğiz, ancak bu sefer tüm headings'i kullanacağız.

    # Parent heading (ve altındaki alt başlıklar) ile ilişkilendirilmiş cümleleri bul
    affected_sentences = heading_system.find_sentences_as_objects(processed_out["sentences"], parent_heading_index)

    # Bu cümleleri tekrar kategorize et, ancak şimdi tüm 'headings' sözlüğünü kullanarak yapıyoruz.
    updated_sentences = categorize_sentences(affected_sentences, headings)

    # Geri dönen updated_sentences'ın headings verilerini tüm processed_out["sentences"] üzerinde güncelle
    processed_out["sentences"] = heading_system.change_sentence_headings(processed_out["sentences"], updated_sentences)

    return processed_out, headings


def process_file(uploaded_file, prompt_text):
    if uploaded_file.type == ("audio/mpeg" or "video/mp4"):
        temp_file_path = ""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name
        sentences = transcript.process_file(temp_file_path)

        text = " ".join(s["translated_text"] for s in sentences)
        headings = generate_headings(text, prompt_text)
        updated_sentences = categorize_sentences(sentences, headings)

        processed_out = {
            "categorized_dict": updated_sentences,
            "sentences": updated_sentences,
            "raw_translated_text": text,
            "headings": headings,
            "type": "audio"
        }

    else:
        text = process_text.read_text_from_file(uploaded_file)
        sentences = process_text.split_into_sentences(text)
        combined_text = " ".join(s["translated_text"] for s in sentences)

        headings = generate_headings(combined_text, prompt_text)
        categorized_dict = categorize_sentences(sentences, headings)

        processed_out = {
            "categorized_dict": categorized_dict,
            "sentences": sentences,
            "raw_translated_text": combined_text,
            "headings": headings,
            "type": "text_file"
        }

    headings = heading_system.sort_headings(headings)
    processed_out["headings"] = headings
    return processed_out, headings

def process_new_file(uploaded_file, prompt_text, existing_headings):
    text = process_text.read_text_from_file(uploaded_file)
    sentences = process_text.split_into_sentences(text)
    combined_text = " ".join(s["translated_text"] for s in sentences)

    categorized_sentences = categorize_sentences(sentences, existing_headings)

    none_count = sum(1 for s in categorized_sentences if s["headings"] == [None])

    if none_count > len(categorized_sentences) / 2:
        # Yeni başlık üret
        new_headings = generate_headings(combined_text, prompt_text)
        categorized_sentences = categorize_sentences(sentences, new_headings)
        current_headings = new_headings
    else:
        current_headings = existing_headings

    current_headings = heading_system.sort_headings(current_headings)

    processed_out_new = {
        "categorized_dict": categorized_sentences,
        "sentences": sentences,
        "raw_translated_text": combined_text,
        "headings": current_headings,
        "type": "text_file"
    }

    return processed_out_new, current_headings

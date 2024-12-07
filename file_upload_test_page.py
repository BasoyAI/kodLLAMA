import streamlit as st
from annotated_text import annotated_text, annotation
import app
import random
import translate


def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


def generate_colored_headings(headings):
    colored_headings = {
        key: [value, random_color()]
        for key, value in headings.items()
    }

    return colored_headings


def show_headings(colored_headings):
    for heading in colored_headings:
        col1, col2 = st.columns([1, 9])
        heading_value = colored_headings[heading][0]
        heading_color = colored_headings[heading][1]
        translated_heading_value = translate.translate_text(heading_value, src_lang='en', dest_lang='tr')
        dot_counter = heading.count(".")
        indent_string_value = "-" * dot_counter * 3
        indent_string_value += ">"
        heading_front_end_value = heading + ". " + translated_heading_value

        with col1:
            if dot_counter == 0:
                st.divider()
            with st.popover(""):
                text_input_key = str(heading) + "_text_input"
                subheader_prompt = st.text_input("Alt başlık promptu giriniz.", key=text_input_key)
                subheader_prompt_translated = "Subheading generating prompt is : " + translate.translate_text(
                    subheader_prompt, "tr", "en")
                if (st.button(" Prompt Üret ", key=heading)):
                    app.generate_subheading_(heading, subheader_prompt_translated)
                    st.session_state["colored_headings"] = generate_colored_headings(app.headings)
                    st.rerun()

        with col2:
            if dot_counter == 0:
                st.divider()
            annotated_text(
                indent_string_value,
                annotation(heading_front_end_value, heading, heading_color),
            )


def get_color_by_heading_id(colored_headings, heading_id):
    for heading in colored_headings:
        if heading == heading_id:
            return colored_headings[heading][1]


def show_text(colored_headings, sentences):
    for sentence in sentences:
        # sentence["headings"] bir liste
        if not sentence.get("headings"):
            # Hiç heading yoksa normal bas
            annotated_text((sentence["text"], "No Heading", "#FFFFFF"))
        else:
            # Birden fazla heading varsa birden fazla annotation ile basabiliriz
            annotations = []
            for h_id in sentence["headings"]:
                if h_id is not None:
                    sentence_color = get_color_by_heading_id(colored_headings, h_id)
                    annotations.append((sentence["text"], str(h_id), sentence_color))
            # annotations birden çok tuple içeriyor, * ile açarak annotated_text'e veriyoruz
            annotated_text(*annotations)



# Başlık durumunu kontrol etmek için session_state kullanıyoruz
if "show_result" not in st.session_state:
    st.session_state["show_result"] = False

# Ana sayfa - Dosya yükleme ve Kategorize Et butonu
if not st.session_state["show_result"]:
    # Streamlit arayüzü
    st.title("Metin Kategorize Uygulaması")
    # Dosya yükleme alanı
    uploaded_file = st.file_uploader("Bir dosya yükleyin", type=["pdf", "docx", "txt", "mp3", "mp4"])
    prompt_text = st.text_area("Enter your prompt here")
    # İşlem butonu
    if st.button("Kategorize Et"):
        if uploaded_file is not None:
            # Dosyayı işleyip başlık ve cümleleri kategorize etme
            app.process_file(uploaded_file, prompt_text)

            st.session_state["colored_headings"] = generate_colored_headings(app.headings)
            st.session_state["categorized_result"] = app.processed_out["categorized_dict"]
            st.session_state["sentences"] = app.processed_out["sentences"]
            st.session_state["show_result"] = True
            st.session_state["headings"] = app.processed_out["headings"]
            st.session_state["file_type"] = app.processed_out["type"]
            st.session_state["raw_translated_text"] = app.processed_out["raw_translated_text"]
            st.session_state["promptText"] = prompt_text

        else:
            st.write("Lütfen bir dosya yükleyin.")
        st.rerun()

# Sonuç sayfası
else:
    st.title("Kategorize Sonuçları")

    colored_headings = st.session_state["colored_headings"]
    col1, col2 = st.columns([1, 2])
    with col1:
        show_headings(colored_headings)
    with col2:
        show_text(colored_headings, st.session_state["sentences"])

    # Sayfa iki sütundan oluşuyor: Sol tarafta başlıklar, sağ tarafta ham metin

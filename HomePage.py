import streamlit as st
from TextCategorize import process_text
from annotated_text import annotated_text
import random
import translate

# Benzersiz renk oluşturma fonksiyonu
def generate_unique_colors(n):
    colors = set()
    while len(colors) < n:
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        colors.add(color)
    return list(colors)

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
            result = process_text(uploaded_file, prompt_text)
            st.session_state["categorized_result"] = result["categorized_dict"]
            st.session_state["sentences"] = result["sentences"]
            st.session_state["show_result"] = True
            st.session_state["headings"] = result["headings"]
            st.session_state["file_type"] = result["type"]

        else:
            st.write("Lütfen bir dosya yükleyin.")

# Sonuç sayfası
else:
    st.title("Kategorize Sonuçları")

    # Sayfa iki sütundan oluşuyor: Sol tarafta başlıklar, sağ tarafta ham metin
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Başlıklar")

        categorized_result = st.session_state["categorized_result"]  # {'Müşteri hiz.': ["fdsg", "dsgggdf"]  }
        headings = st.session_state["headings"]
        num_titles = len(headings)
        
        # Her başlık için benzersiz renkler oluşturma
        unique_colors = generate_unique_colors(num_titles)
        
        # Başlık ve renkleri eşleştirmek için bir sözlük oluşturma
        title_colors = {}
        for i, (title, color) in enumerate(zip(headings, unique_colors), 1):
            title_label = str(i)
            title_colors[title] = (color, title_label)
            annotated_text((translate.translate_text(title, src_lang='en', dest_lang='tr'), title_label, color))

    with col2:
        st.subheader("Orijinal Metin")

        # Sıralı şekilde cümleleri vurgulamak için dizin oluştur
        highlighted_sentences = []
        file_type = st.session_state["file_type"]
        if file_type is "audio":
            for sentence in categorized_result:
                color, label = title_colors[sentence.get("heading")]
                highlighted_sentences.append((sentence["text"], label, color))
        else:
            # st.session_state["sentences"] sıralamasına göre cümleleri vurgulama
            for sentence in st.session_state["sentences"]:
                # Hangi başlığa ait olduğunu bul
                for title, sentences in categorized_result.items():
                    if sentence in sentences:
                        color, label = title_colors[title]
                        highlighted_sentences.append((sentence, label, color))
                        break

            # Cümleleri tek satır halinde göster
        annotated_text(*highlighted_sentences)

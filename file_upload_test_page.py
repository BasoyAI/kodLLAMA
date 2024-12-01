import streamlit as st
from annotated_text import annotated_text
import app


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
    st.divider()
    st.write(st.session_state["categorized_result"])
    st.divider()
    st.write(st.session_state["sentences"]) 
    st.divider()
    st.write(st.session_state["show_result"]) 
    st.divider()
    st.write(st.session_state["headings"]) 
    st.divider()
    st.write(st.session_state["file_type"]) 
    st.divider()
    st.write(st.session_state["raw_translated_text"]) 
    st.divider()
    st.write(st.session_state["promptText"])

    # Sayfa iki sütundan oluşuyor: Sol tarafta başlıklar, sağ tarafta ham metin
    

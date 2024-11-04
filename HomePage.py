import streamlit as st
from TextCategorize import process_text
from annotated_text import annotated_text
import random
import http

# Benzersiz renk oluşturma fonksiyonu
def generate_unique_colors(n):
    colors = set()
    while len(colors) < n:
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))  # Rastgele bir HEX renk oluştur
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

    # İşlem butonu
    if st.button("Kategorize Et"):
        if uploaded_file is not None:
            # Dosyayı işleyip başlık ve cümleleri kategorize etme
            result = process_text(uploaded_file)
            st.session_state["categorized_result"] = result["categorized_dict"]
            st.session_state["sentences"] = result["sentences"]
            st.session_state["show_result"] = True  # Sonuç sayfasına geçmek için durumu güncelleme
        else:
            st.write("Lütfen bir dosya yükleyin.")

# Sonuç sayfası
else:
    st.title("Kategorize Sonuçları")

    # Sayfa iki sütundan oluşuyor: Sol tarafta başlıklar, sağ tarafta ham metin
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Başlıklar")

        categorized_result = st.session_state["categorized_result"]
        num_titles = len(categorized_result.keys())
        
        # Her başlık için benzersiz renkler oluşturma
        unique_colors = generate_unique_colors(num_titles)
        
        # Başlık ve renkleri eşleştirmek için bir sözlük oluşturma
        title_colors = {}
        for i, (title, color) in enumerate(zip(categorized_result.keys(), unique_colors), 1):
            title_label = str(i)  # Başlık numarasını label olarak kullan
            title_colors[title] = (color, title_label)  # Başlığa renk ve numara ata
            annotated_text((title, title_label, color))  # Başlık ve label olarak numara göster

    with col2:
        st.subheader("Orijinal Metin")

        # Cümleleri ilgili başlıkların rengi ve numarasıyla vurgulamak için Annotated Text kullanma
        highlighted_sentences = []
        
        for title, sentences in categorized_result.items():
            color, label = title_colors[title]  # Başlığın rengini ve numarasını al
            for sentence in sentences:
                highlighted_sentences.append((sentence, label, color))  # Cümleyi başlığın rengi ve numarasıyla ekle
        
        # Cümleleri tek satır halinde göster
        annotated_text(*highlighted_sentences)

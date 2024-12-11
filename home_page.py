import streamlit as st
from annotated_text import annotated_text
import app
import random
import translate
import json

from ai import chat_response
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(layout="wide")

def random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def generate_colored_headings(headings):
    if headings is None:
        headings = {}
    return {
        key: [value, random_color()]
        for key, value in headings.items()
    }

def show_headings(colored_headings, prefix="", doc_key=None):
    for heading in colored_headings:
        st.divider()
        
        heading_value = colored_headings[heading][0]
        heading_color = colored_headings[heading][1]
        translated_heading_value = translate.translate_text(heading_value, src_lang='en', dest_lang='tr')
        heading_front_end_value = f"{heading}. {translated_heading_value}"

        st.markdown(
            f"<div style='color: {heading_color}; font-weight: bold; font-size: 16px; padding: 5px;'>{heading_front_end_value}</div>",
            unsafe_allow_html=True
        )

        # Alt başlık oluşturma
        with st.expander("Alt başlık oluştur", expanded=False):
            text_input_key = prefix + str(heading) + "_text_input"
            subheader_prompt = st.text_input("Alt başlık promptu giriniz.", key=text_input_key)
            subheader_prompt_translated = "Subheading generating prompt is : " + translate.translate_text(
                subheader_prompt, "tr", "en")
            button_key = prefix + heading + "_button"
            if st.button("Başlık Üret", key=button_key):
                # Eski belge için doc_key None, yeni belgeler için doc_key örn: "new_doc_1"
                if doc_key is None:
                    # Eski belgedeyiz
                    current_processed_out = st.session_state["processed_out"]
                    current_headings = st.session_state["headings"]
                    prompt_text = st.session_state["promptText"]
                    updated_processed_out, updated_headings = app.generate_subheading_(
                        heading,
                        subheader_prompt_translated,
                        current_processed_out,
                        current_headings,
                        prompt_text
                    )
                    st.session_state["processed_out"] = updated_processed_out
                    st.session_state["headings"] = updated_headings
                    st.session_state["colored_headings"] = generate_colored_headings(updated_headings)
                else:
                    # Yeni belge
                    current_processed_out = st.session_state["new_file_uploaded_dict"][doc_key]
                    current_headings = current_processed_out["headings"]
                    prompt_text = st.session_state["promptText"]
                    updated_processed_out, updated_headings = app.generate_subheading_(
                        heading,
                        subheader_prompt_translated,
                        current_processed_out,
                        current_headings,
                        prompt_text
                    )
                    st.session_state["new_file_uploaded_dict"][doc_key] = updated_processed_out
                    st.session_state[f"colored_headings_{doc_key}"] = generate_colored_headings(updated_headings)

                st.rerun()
    # Ana Başlık Oluştur butonu ekleme
    st.divider()
    with st.expander("Ana Başlık Oluştur", expanded=False):
        main_heading_prompt_key = prefix + "_main_heading_text_input"
        main_heading_prompt = st.text_input("Ana başlık promptu giriniz.", key=main_heading_prompt_key)
        main_heading_prompt_translated = "Main heading generating prompt is : " + translate.translate_text(
            main_heading_prompt, "tr", "en")
        main_button_key = prefix + "_main_heading_button"
        if st.button("Ana Başlık Üret", key=main_button_key):
            if doc_key is None:
                current_processed_out = st.session_state["processed_out"]
                current_headings = st.session_state["headings"]
                prompt_text = st.session_state["promptText"]
                updated_processed_out, updated_headings = app.generate_main_heading(
                    main_heading_prompt_translated,
                    current_processed_out,
                    current_headings,
                    prompt_text
                )
                st.session_state["processed_out"] = updated_processed_out
                st.session_state["headings"] = updated_headings
                st.session_state["colored_headings"] = generate_colored_headings(updated_headings)
            else:
                current_processed_out = st.session_state["new_file_uploaded_dict"][doc_key]
                current_headings = current_processed_out["headings"]
                prompt_text = st.session_state["promptText"]
                updated_processed_out, updated_headings = app.generate_main_heading(
                    main_heading_prompt_translated,
                    current_processed_out,
                    current_headings,
                    prompt_text
                )
                st.session_state["new_file_uploaded_dict"][doc_key] = updated_processed_out
                st.session_state[f"colored_headings_{doc_key}"] = generate_colored_headings(updated_headings)

            st.rerun()


def get_color_by_heading_id(colored_headings, heading_id):
    for key,value in colored_headings.items():
        if key == heading_id:
            return colored_headings[key][1]

def show_text(colored_headings, sentences):
    for sentence in sentences:
        if not sentence.get("headings"):
            annotated_text((sentence["text"], "No Heading", "#FFFFFF"))
        else:
            annotations = []
            for h_id in sentence["headings"]:
                sentence_color = get_color_by_heading_id(colored_headings, h_id)
                annotations.append((sentence["text"], str(h_id), sentence_color))
            annotated_text(*annotations)

def show_ai_chat(sentences, headings, doc_key):
    # Ensure `st.session_state.chat_histories` exists and initialize it if needed
    if 'chat_histories' not in st.session_state:
        st.session_state.chat_histories = []

    # Extend the list to accommodate the index `doc_key` if needed
    while len(st.session_state.chat_histories) <= doc_key:
        st.session_state.chat_histories.append([])

    # Process sentences with headings
    sentences_with_headings = []
    for i, sentence in enumerate(sentences):
        for heading in headings:
            if sentence["headings"] == heading:
                sentences_with_headings.append({"sentence": sentence, "headings": heading.value})

    # Combine the translated text into one string
    content_text = " ".join(sentence["translated_text"] for sentence in sentences)

    # Display the chatbot interface header
    st.header("KodLLAMA'ya Sor!")

    # Track if the chat history has been updated
    chat_updated = False
    
    human_message=""
    ai_message=""
    for message in st.session_state.chat_histories[doc_key]:
        if isinstance(message, HumanMessage):
            translated_content = translate.translate_text(message.content, "en", "tr")
            st.chat_message("user").markdown(translated_content)
        elif isinstance(message, AIMessage):
            translated_content = translate.translate_text(message.content, "en", "tr")
            with st.chat_message("assistant"):
                st.markdown(translated_content)

    # Handle user input via the Streamlit chat input
    if prompt := st.chat_input("Nasıl yardımcı olabilirim?", key=doc_key):
        # Display the user's message
        st.chat_message("user").markdown(prompt)

        # Translate the user's message and get the AI's response
        translated_prompt = translate.translate_text(prompt, "tr", "en")
        response = chat_response(translated_prompt, content_text, st.session_state.chat_histories[doc_key])
        translated_response = translate.translate_text(response, "en", "tr")

        # Display the AI's response
        with st.chat_message("assistant"):
            st.markdown(translated_response)
        st.rerun()

        # Append the assistant's response to the chat history
       


if "show_result" not in st.session_state:
    st.session_state["show_result"] = False
if "num_new_docs" not in st.session_state:
    st.session_state["num_new_docs"] = 0
if "new_file_uploaded_dict" not in st.session_state:
    st.session_state["new_file_uploaded_dict"] = {}
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = []

st.title("kodLLAMA")

if not st.session_state["show_result"]:
    uploaded_file = st.file_uploader("Bir dosya yükleyin", type=["pdf", "docx", "txt", "mp3", "mp4"])
    prompt_text = st.text_area("Enter your prompt here")

    if st.button("Kategorize Et"):
        if uploaded_file is not None:
            processed_out, headings = app.process_file(uploaded_file, prompt_text)

            st.session_state["processed_out"] = processed_out
            st.session_state["headings"] = headings
            st.session_state["colored_headings"] = generate_colored_headings(headings)
            st.session_state["categorized_result"] = processed_out["categorized_dict"]
            st.session_state["sentences"] = processed_out["sentences"]
            st.session_state["show_result"] = True
            st.session_state["file_type"] = processed_out["type"]
            st.session_state["raw_translated_text"] = processed_out["raw_translated_text"]
            st.session_state["promptText"] = prompt_text
            st.rerun()
else:
    base_tabs = ["Eski Belge"]
    new_doc_tabs = [f"Yeni Belge {i}" for i in range(1, st.session_state["num_new_docs"] + 1)]
    all_tabs = base_tabs + new_doc_tabs

    top_col1, top_col2 = st.columns([10, 1])
    with top_col1:
        tabs = st.tabs(all_tabs)
    with top_col2:
        if st.button("➕"):
            st.session_state["num_new_docs"] += 1
            st.rerun()

    # Eski Belge Tab
    with tabs[0]:
        left_col, middle_col, right_col = st.columns([1.5, 5, 3])
        with left_col:
            show_headings(st.session_state["colored_headings"], prefix="old_", doc_key=None)
        with middle_col:
            show_text(st.session_state["colored_headings"], st.session_state["sentences"])
        with right_col:
            show_ai_chat(st.session_state["sentences"], st.session_state["headings"], 0)


    # Yeni Belgeler Tab
    for i, tab_name in enumerate(new_doc_tabs, start=1):
        doc_key = f"new_doc_{i}"
        with tabs[i]:
            if doc_key not in st.session_state["new_file_uploaded_dict"]:
                new_uploaded_file = st.file_uploader("Yeni doküman yükleyin", type=["pdf", "docx", "txt", "mp3", "mp4"],
                                                     key=f"uploader_{doc_key}")
                if new_uploaded_file is not None:
                    if st.button("Yeni Dokümanı Kategorize Et", key=f"process_button_{doc_key}"):
                        processed_out_new, new_headings = app.process_new_file(new_uploaded_file, st.session_state["promptText"],
                                                                               st.session_state["headings"])
                        st.session_state["new_file_uploaded_dict"][doc_key] = processed_out_new
                        st.session_state[f"colored_headings_{doc_key}"] = generate_colored_headings(new_headings)
                        st.rerun()
            else:
                processed_out_new = st.session_state["new_file_uploaded_dict"][doc_key]
                left_col_new, middle_col_new, right_col_for_ai = st.columns([1.5, 5, 3])
                with left_col_new:
                    if f"colored_headings_{doc_key}" not in st.session_state:
                        st.warning("Başlıklar yüklenemedi. Lütfen belgeyi tekrar yükleyin.")
                    else:
                        show_headings(st.session_state[f"colored_headings_{doc_key}"], prefix=f"new_{i}_", doc_key=doc_key)
                with middle_col_new:
                    show_text(st.session_state[f"colored_headings_{doc_key}"], processed_out_new["sentences"])
                with right_col_for_ai:
                    show_ai_chat(processed_out_new["sentences"], processed_out_new["headings"], i)
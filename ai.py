from typing import List
from ollama import chat
import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field

# Define the structured output schema
class HeadingsOutput(BaseModel):
    titles: List[str] = Field(
        description="A list of titles derived from the text. Each title should be no more than five words."
    )

llm = ChatOllama(model="llama3.2", temperature=0.1, num_ctx=8192)
structured_llm = llm.with_structured_output(HeadingsOutput)


def chat_response(prompt, text, chat_history):
    # İlk konuşma için uygun mesajı oluştur
    if len(chat_history) <= 0:
        prompt_message = f"""
            You are an integrated chatbot for a website capable of text analysis. 
            Users will upload texts to the system and ask you questions about them. 
            You will analyze the text in depth and provide clear, accurate, and relevant answers to their questions based on the content of the text.
            \nThe uploaded text is:
            \n{text}
            \n\nUser's prompt is:
            \n{prompt}
        """
    else:
        # Konuşma geçmişi varsa sadece prompt'u kullan
        prompt_message = prompt

    # Prompt şablonunu tanımla
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Your name is KodLLAMA. You are a chatbot that can analyze documents.",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )

    # Şablonu ve dil modelini birleştirerek zinciri oluştur
    chain = prompt_template | llm

    # Yapay zekadan yanıt al
    response = chain.invoke({"input": prompt_message, "chat_history": chat_history})
    content_value = response.content if hasattr(response, 'content') else str(response)

    # Yanıtın string formatında olduğundan emin ol
    response = str(response)

    # Mesajları konuşma geçmişine ekle
    chat_history.append(HumanMessage(content=prompt_message))
    chat_history.append(AIMessage(content=content_value))
    print(chat_history)
    return content_value

def generate_main_heading_(text, promptText, headings: dict):
    heading_strings = ", ".join(headings.values())
    messages = [
        {
            'role': 'user',
            'content': (
                "You are a bot that analyzes texts. Your task is to generate a suitable title for the provided text. "
                "The title should be no more than five words. Please provide only the subtitle as output. "
                "Do not add number to subtitle or any comments. "
                f"You can not create the same with any of these titles: {heading_strings}. "
                f"The topic of the provided text and your task is as follows: '{promptText}', and the text is: '{text}'."
            )
        },
    ]

    response = chat('llama3.2', messages=messages)
    created_main_title = response['message']['content'].strip()
    return created_main_title


def generate_subheading(text, promptText, heading, headings: dict):
    heading_strings = ", ".join(headings.values())
    messages = [
        {
            'role': 'user',
            'content': (
                "You are a bot that analyzes texts. Your task is to generate a suitable subtitle for the provided text. "
                "Each title should be no more than five words. Please provide only the subtitle as output. "
                "Do not add number to subtitle or any comments. "
                f"You can not create the same with any of these titles: {heading_strings}. "
                f"You must create a relative subtitle with the main title and text. The main title is: '{heading}'. "
                f"The topic of the provided text and your task is as follows: '{promptText}', and the text is: '{text}'."
            )
        },
    ]

    response = chat('llama3.2', messages=messages)
    created_subtitle = response['message']['content'].strip()
    return created_subtitle

def generate_headings(text, promptText):
    prompt = (f"You are a bot that analyzes texts. Your task is to generate suitable titles for the provided text. You "
              f"need to analyze the text and create the most appropriate titles. Do not generate any subtitles:\n\n "
              f"The topic of the provided text and your task is as follows: '{promptText}', and the text is as "
              f"follows:\n\n \"\"\"{text}\"\"\".")

    response = structured_llm.invoke(prompt)
    headings = response.titles

    # Sözlük oluşturma
    cleaned_headings = {}
    for i, heading in enumerate(headings):
        # Eğer başlık numaralı ise numarayı kaldır
        if len(heading) >= 3 and heading[0].isdigit() and heading[1] == '.' and heading[2] == ' ':
            heading_name = heading[3:]
        else:
            heading_name = heading

        cleaned_headings[str(i + 1)] = heading_name

    return cleaned_headings

def categorize_sentences(sentences, headings):
    heading_indices = {str(i): heading for i, heading in enumerate(headings.values())}

    for sentence in sentences:
        translated_sentence = sentence["translated_text"]
        messages = [
            {
                'role': 'user',
                'content': (
                    "From the following headings, identify all that are suitable for the given sentence. "
                    "If the sentence clearly aligns with multiple headings, return all their indices as a comma-separated list (e.g. '1, 3'). "
                    "If it only aligns with a single heading, return just that one heading index. "
                    "If the sentence does not match any heading, return 'none'. "
                    "Do not add extra commentary.\n\n"
                    f"Sentence: \"{translated_sentence}\"\n"
                    f"Headings: {json.dumps(heading_indices)}"
                )
            },
        ]
        response = chat('llama3.2', messages=messages)
        chosen_indexes = response['message']['content'].strip()

        chosen_indexes = [idx.strip() for idx in chosen_indexes.split(",") if idx.strip() in heading_indices.keys()]

        if not chosen_indexes:
            sentence["headings"] = []
            sentence["headings"].append(None)
            continue

        sentence["headings"] = []
        for ch_idx in chosen_indexes:
            matched_heading = heading_indices[ch_idx]
            index = None
            for key, value in headings.items():
                if value == matched_heading:
                    index = key
                    break
            sentence["headings"].append(str(index))
    return sentences



def categorize_with_single_heading(sentences, heading, heading_index, headings):
    for sentence in sentences:
        translated_sentence = sentence["translated_text"]
        messages = [
            {
                'role': 'user',
                'content': (
                    "Evaluate whether the given sentence is specifically and strongly related to the provided heading.\n\n"
                    f"Heading: \"{heading}\"\n"
                    f"Other existing headings: {', '.join(headings.keys())}\n\n"
                    "Guidelines:\n"
                    "- The sentence should only be assigned to this heading if it is highly relevant and fits clearly under this category.\n"
                    "- Consider the semantic meaning of the sentence and ensure it does not overlap significantly with other headings.\n"
                    "- Be selective and assign the sentence only if it directly supports or aligns with the key idea of this heading.\n\n"
                    "Instructions:\n"
                    "- Respond with '1' if the sentence is clearly and strongly related to this heading.\n"
                    "- Respond with '0' if the sentence is not sufficiently relevant or if its relevance is ambiguous.\n"
                    "- Do not include any additional explanations or commentary.\n\n"
                    f"Sentence: \"{translated_sentence}\""
                )
            },
        ]
        response = chat('llama3.2', messages=messages)
        is_related = response['message']['content'].strip()

        if is_related == "1":
            if "headings" not in sentence:
                sentence["headings"] = []
            sentence["headings"].append(heading_index)

    return sentences



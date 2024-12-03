from typing import List

from ollama import chat
import json

from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field


# Define the structured output schema
class HeadingsOutput(BaseModel):
    titles: List[str] = Field(
        description="A list of titles derived from the text. Each title should be no more than five words."
    )


llm = ChatOllama(model="llama3.2", temperature=0.1, num_ctx=8192)
structured_llm = llm.with_structured_output(HeadingsOutput)


def generate_subheading(text, promptText, heading, headings: dict):
    heading_strings = ", ".join(headings.values())
    messages = [
        {
            'role': 'user',
            'content': (
                "You are a bot that analyzes texts. Your task is to generate suitable subtitle for the provided text. "
                "You need to analyze the text and create the most appropriate subtitle. "
                "Each title should be no more than five words. Please provide only the subtite as output. "
                "Do not add number to subtitle or add any comments. "
                f"You can not create the same with any of these titles: {heading_strings}."
                f"You must create a relative subtitle with the main title and text. The main title is: '{heading}'"
                f"The topic of the provided text and your task is as follows: '{promptText}', and the text is as follows: '{text}'."
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

        # Dictionary'e başlık ve boş bir liste ekle
        cleaned_headings[str(i + 1)] = heading_name

    return cleaned_headings


def categorize_sentences(sentences, headings):
    heading_indices = {str(i): heading for i, heading in enumerate(headings.values())}

    print(f"Headings: {headings}")
    print(f"Indexed Headings: {heading_indices}")

    for sentence in sentences:
        translated_sentence = sentence["translated_text"]
        messages = [
            {
                'role': 'user',
                'content': (
                    "Choose the index of the heading that this sentence fits. "
                    "You will see the headings below, but you must respond with only the index of the heading. "
                    "Do not make any comments or write other characters.\n\n "
                    f"Sentence: \"{translated_sentence}\" \n"
                    f"Headings: {json.dumps(heading_indices)}"
                )
            },
        ]
        response = chat('llama3.2', messages=messages)
        chosen_index = response['message']['content'].strip()
        print(f"message is:  {messages}  \n  response is: {response}")
        # Check if the index returned by the model is valid
        if chosen_index in heading_indices.keys():
            matched_heading = heading_indices[chosen_index]
            index = None
            for key, value in headings.items():  #TODO: change this
                if value == matched_heading:
                    index = key
            sentence["heading"] = str(index)
        else:
            # If the model returns an invalid index, add it to the "none" category.
            print(f"Error: Index '{chosen_index}' not found. Could not categorize sentence: '{sentence}'")
            if not sentence.get("heading"):
                sentence["heading"] = None
    return sentences

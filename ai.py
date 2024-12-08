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

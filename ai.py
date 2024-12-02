from ollama import chat

def generate_subheading(text, promptText, heading, headings: dict):
    messages = [
        {
            'role': 'user',
            'content': (
                "You are a bot that analyzes texts. Your task is to generate suitable subtitle for the provided text. "
                "You need to analyze the text and create the most appropriate subtitle. "
                "Each title should be no more than five words. Please provide only the subtite as output. "
                "Do not add number to subtitle or add any comments. "
                f"You can not create the same with any of these titles: {", ".join(headings.values())}."
                f"You must create a relative subtitle with the main title and text. The main title is: '{heading}'"
                f"The topic of the provided text and your task is as follows: '{promptText}', and the text is as follows: '{text}'."
            )
        },
    ]

    response = chat('llama3.2', messages=messages)
    created_subtitle = response['message']['content'].strip()
    return created_subtitle

def generate_headings(text, promptText):
    messages = [
        {
            'role': 'user',
            'content': (
                "You are a bot that analyzes texts. Your task is to generate suitable titles for the provided text. "
                "You need to analyze the text and create the most appropriate titles. Do not generate any subtitles. "
                "Each title should be no more than five words. Please provide only the titles as output. "
                "Do not number them or add any comments. "
                f"The topic of the provided text and your task is as follows: '{promptText}', and the text is as follows: '{text}'."
            )
        },
    ]
    
    response = chat('llama3.2', messages=messages)
    headings = response['message']['content'].strip().split("\n")
    headings = [heading.strip() for heading in headings if heading.strip()]

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


def categorize_sentences(sentences, headings: dict):
    for sentence in sentences:
        # Prepare the AI prompt with heading names
        messages = [
            {
                'role': 'user',
                'content': f'Choose one heading that this sentence fits. Your response must be only the heading that you choose. Do not make any comments or write other characters. Sentence: "{sentence["translated_text"]}" Headings: {", ".join(headings.values())}'
            },
        ]
        response = chat('llama3.2', messages=messages)
        chosen_title = response['message']['content'].strip()

        # Find the corresponding index for the chosen title
        chosen_index = next((index for index, title in headings.items() if title == chosen_title), None)

        if chosen_index:
            sentence["heading"] = chosen_index  # Assign the index instead of the title
        else:
            sentence["heading"] = "None"  # Handle unmatched headings
            print(
                f"Error: Heading '{chosen_title}' not found. Could not categorize sentence: '{sentence['translated_text']}'")

    return sentences



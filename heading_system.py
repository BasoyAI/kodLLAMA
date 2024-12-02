# Import the test data from app.py
def get_subheadings(parent_index, heading_list):
    """
    Retrieves all subheadings under a given parent index.

    Args:
        parent_index (str): The parent heading index (e.g., "1.1").
        heading_list (dict): Dictionary containing heading hierarchy.

    Returns:
        list: A list of names of the parent heading and its subheadings.
        :param parent_index:
        :param heading_list:
    """
    # List to store the subheadings
    subheadings = []

    # Iterate over the headings to find those starting with the parent index
    for key, value in heading_list.items():
        if key.startswith(parent_index):
            subheadings.append(value)

    return subheadings


def generate_heading_index(heading_list, parent_index=None):
    """
    Generates a new heading index based on the existing headings.

    Args:
        heading_list (dict): Dictionary containing the heading hierarchy.
        parent_index (str, optional): Parent heading index (e.g., "1" or "1.2").

    Returns:
        str: A new heading index.
    """
    if parent_index:
        # Find all subheadings that start with the given parent index
        subheadings = [key for key in heading_list.keys() if key.startswith(f"{parent_index}.")]

        if subheadings:
            # Extract the last subheading index after the parent index
            last_index = max(int(key.split(".")[-1]) for key in subheadings)
            # Generate the next subheading index
            return f"{parent_index}.{last_index + 1}"
        else:
            # If no subheadings exist under the parent, start with ".1"
            return f"{parent_index}.1"
    else:
        # Find the highest top-level index
        top_level_indices = [int(key.split(".")[0]) for key in heading_list.keys() if "." not in key]

        if top_level_indices:
            # Return the next top-level index
            return str(max(top_level_indices) + 1)
        else:
            # If no top-level headings exist, start with "1"
            return "1"

def find_sentences(sentence_list, heading_index, language="text"):
    """
    Finds all sentences in the sentence_list with the specified heading_index.

    Args:
        sentence_list (list): List of sentence dictionaries.
        heading_index (str): The heading index to match.
        language (str): Specifies which text to retrieve ('text' or 'translated_text').

    Returns:
        list: List of texts that match the heading_index in the specified language.
    """
    # Validate the language parameter
    if language not in ["text", "translated_text"]:
        raise ValueError("Invalid language parameter. Use 'text' or 'translated_text'.")

    # Filter the sentences that match the heading index
    return [sentence[language] for sentence in sentence_list if sentence["heading"] == heading_index]



def find_sentences_with_sub(sentence_list, heading_list, heading_index, language="text"):
    """
    Finds all sentences in the sentence_list with the specified heading_index
    or any of its subheadings.

    Args:
        sentence_list (list): List of sentence dictionaries.
        headings (dict): Dictionary containing heading hierarchy.
        heading_index (str): The parent heading index to match, including subheadings.
        language (str): Specifies which text to retrieve ('text' or 'translated_text').

    Returns:
        list: List of texts that match the heading_index or its subheadings in the specified language.
        :param language:
        :param heading_index:
        :param sentence_list:
        :param heading_list:
    """
    # Validate the language parameter
    if language not in ["text", "translated_text"]:
        raise ValueError("Invalid language parameter. Use 'text' or 'translated_text'.")

    # Find all subheadings under the parent index
    subheading_indices = [
        key for key in heading_list.keys() if key.startswith(heading_index)
    ]

    # Filter the sentences that match the parent index or any of its subheadings
    return [sentence[language] for sentence in sentence_list if sentence["heading"] in subheading_indices]

def convert_index_for_ai(heading_list):
    """
    Converts the hierarchical index of headings to a flat sequential index for AI processing.

    Args:
        heading_list (dict): Original headings dictionary with hierarchical indices.

    Returns:
        dict: New headings dictionary with sequential indices.
    """
    # Initialize a new dictionary to store the transformed headings
    new_headings = {}

    # Use an incremental counter for the new indices
    counter = 1

    # Iterate through the original headings in order
    for _, heading_name in sorted(heading_list.items()):
        # Assign a new sequential index to each heading
        new_headings[str(counter)] = heading_name
        counter += 1

    return new_headings

def find_sentences_as_objects(sentence_list, heading_index):
    """
    Finds all sentences in the sentence_list with the specified heading_index,
    returning them as structured objects.

    Args:
        sentence_list (list): List of sentence dictionaries.
        heading_index (str): The heading index to match.

    Returns:
        list: List of sentence dictionaries that match the heading_index.
    """
    # Filter the sentences that match the heading index
    return [sentence for sentence in sentence_list if sentence["heading"] == heading_index]


def sort_headings(heading_list):
    """
    Sorts a dictionary of headings by their hierarchical keys.

    Args:
        heading_list (dict): Dictionary containing heading indices and their corresponding titles.

    Returns:
        dict: A new dictionary with headings sorted by their hierarchical keys.
    """
    # Sort the dictionary keys using natural sorting for hierarchical structure
    sorted_keys = sorted(heading_list.keys(), key=lambda x: list(map(int, x.split("."))))

    # Create a new dictionary with sorted keys
    sorted_headings = {key: heading_list[key] for key in sorted_keys}

    return sorted_headings


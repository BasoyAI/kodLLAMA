# Import the test data from app.py
from app import headings, sentences_list

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

def find_sentences(sentence_list, heading_list, heading_index, language="text"):
    """
    Finds all sentences in the sentence_list with the specified heading_index.

    Args:
        sentence_list (list): List of sentence dictionaries.
        heading_list (dict): Dictionary containing heading hierarchy.
        heading_index (str): The heading index to match.
        language (str): Specifies which text to retrieve ('text' or 'translated_text').

    Returns:
        list: List of texts that match the heading_index in the specified language.
    """
    # Get the heading name from the heading list
    heading_name = heading_list.get(heading_index)
    if not heading_name:
        return []

    # Validate the language parameter
    if language not in ["text", "translated_text"]:
        raise ValueError("Invalid language parameter. Use 'text' or 'translated_text'.")

    # Filter the sentences that match the heading name
    return [sentence[language] for sentence in sentence_list if sentence["heading"] == heading_name]


def find_sentences_with_sub(sentence_list, heading_list, heading_index, language="text"):
    """
    Finds all sentences in the sentence_list with the specified heading_index
    or any of its subheadings.

    Args:
        sentence_list (list): List of sentence dictionaries.
        heading_list (dict): Dictionary containing heading hierarchy.
        heading_index (str): The parent heading index to match, including subheadings.
        language (str): Specifies which text to retrieve ('text' or 'translated_text').

    Returns:
        list: List of texts that match the heading_index or its subheadings in the specified language.
    """
    # Get the names of the parent heading and all its subheadings
    subheading_names = [
        name for key, name in heading_list.items() if key.startswith(heading_index)
    ]

    # Validate the language parameter
    if language not in ["text", "translated_text"]:
        raise ValueError("Invalid language parameter. Use 'text' or 'translated_text'.")

    # Filter the sentences that match any of these names
    return [sentence[language] for sentence in sentence_list if sentence["heading"] in subheading_names]




# Example usage for testing
if __name__ == "__main__":
    # Test the function get_subheadings
    result = get_subheadings("1", headings)
    print("Subheadings under '1.2':", result)

    # Test the function generate_heading_index
    print("Next top-level index:", generate_heading_index(headings))  # Expected output: "2"
    print("Next index under '1':", generate_heading_index(headings, "1"))  # Expected output: "1.4"
    print("Next index under '1.2':", generate_heading_index(headings, "1.2"))  # Expected output: "1.2.2"

    # Test the function find_sentences
    print("Sentences with heading '1.2':", find_sentences(sentences_list, headings,"1.2"))

    # Test the function find_sentences_with_sub
    print("Sentences with heading '1.2' and its subheadings:", find_sentences_with_sub(sentences_list, headings,"1.2"))


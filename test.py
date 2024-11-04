import json
import re

# Sample transcription JSON data
transcription = [
    {"start": "00:00:00", "end": "00:00:03", "text": "Hayvanlar için hayatlarını? tehlikeye atmaya. hazır insanlar var!"},
    {"start": "00:00:03", "end": "00:00:06", "text": "Ayni zamanda tuhaf, kötü ve cirkin icinde"},
    {"start": "00:00:06", "end": "00:00:12", "text": "Bu en tuhaf ve en ölúmcül hayvanlara ev sahipligi yapan cennet bahçelerine"},
    {"start": "00:00:12", "end": "00:00:16", "text": "ve yer yüzündeki,en-tehlikeli-islerin yapildigi is yerine dogru bir yolculuk."}
]

# Initialize a list to store the final sentences
final_sentences = []
current_sentence = ""
current_start = transcription[0]["start"]

# Loop over each segment
for i, segment in enumerate(transcription):
    # Update the current start time for each new segment
    if not current_sentence:
        current_start = segment["start"]
    
    # Split text by sentence-ending punctuation (., !, ?, ...)
    # Treat "..." as a single sentence-ending symbol
    sentences = re.split(r'(?<=[.!?…])(?<!\.\.\.)\s*', segment["text"])
    
    # Process each split part (sentence)
    for j, part in enumerate(sentences):
        # Ignore empty parts
        if part.strip():
            # Add this part to the current sentence
            current_sentence += part.strip()
        
        # Check if this is the last part and doesn't end with a punctuation mark
        if j == len(sentences) - 1 and not re.search(r'[.!?…]$', segment["text"]):
            current_sentence = current_sentence.rstrip(".!?…")
        
        # If a sentence ends (i.e., we encounter punctuation at the end), save it
        if re.search(r'[.!?…]$', current_sentence):
            # Use the segment's end time only if this is the last sentence of the segment; otherwise, keep the start time the same
            end_time = segment["end"] if (j == len(sentences) - 1) else segment["end"]
            # Append the completed sentence to the final list
            final_sentences.append({"start": current_start, "end": end_time, "text": current_sentence.strip()})
            # Reset for the next sentence
            current_sentence = ""
            # Update start time only for the first sentence in the new segment or the first split sentence within this segment
            if j < len(sentences) - 1:
                current_start = segment["start"]

# Print or save the final sentences
print(json.dumps(final_sentences, ensure_ascii=False, indent=4))

import re
import whisper
import moviepy
import os
import translate


# Function to convert MP4 to MP3
def convert_to_mp3(file_path):
    if file_path.endswith('.mp4'):
        clip = moviepy.editor.VideoFileClip(file_path)
        mp3_path = file_path.replace('.mp4', '.mp3')
        clip.audio.write_audiofile(mp3_path)
        return mp3_path
    return file_path


# Function to transcribe with Whisper
def transcribe_audio(file_path) -> list:
    model = whisper.load_model("small")
    result = model.transcribe(file_path)
    transcriptions = []

    for segment in result['segments']:
        start_time = format_time(segment['start'])
        end_time = format_time(segment['end'])
        text = segment['text']
        part = {"start": start_time, "end": end_time, "text": text}
        transcriptions.append(part)

    return transcriptions


# Function to format time in hh:mm:ss
def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02}:{mins:02}:{secs:02}"


# Main processing function
def process_file(file_path):
    mp3_path = convert_to_mp3(file_path)
    transcription = format_transcript(mp3_path)

    # Output the transcription with timestamps
    for line in transcription:
        print(line)

    return transcription


def format_transcript(file_path) -> list[dict]:
    transcription = transcribe_audio(file_path)
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
                print(current_sentence.strip())
                translated_text = translate.translate_text(current_sentence.strip(), "tr", "en")
                final_sentences.append({"id": j, "start": current_start, "end": end_time, "text": current_sentence.strip(),
                                        "translated_text": translated_text})
                # Reset for the next sentence
                current_sentence = ""
                # Update start time only for the first sentence in the new segment or the first split sentence within this segment
                if j < len(sentences) - 1:
                    current_start = segment["start"]

    return final_sentences

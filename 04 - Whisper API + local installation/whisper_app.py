import streamlit as st
import whisper
import os

def transcribe_audio(audio_path):
    """Transcribes a static MP3 file using OpenAI's Whisper model."""
    model = whisper.load_model("base")  # Load the Whisper model
    result = model.transcribe(audio_path)
    return result["text"]

# Streamlit UI
st.title("Whisper AI - Static Audio Transcription")
st.write("This app transcribes a predefined MP3 audio file using OpenAI's Whisper model.")

# Define static audio file path
STATIC_AUDIO_PATH = "static_audio.mp3"  # Ensure this file exists in your project folder

if os.path.exists(STATIC_AUDIO_PATH):
    st.audio(STATIC_AUDIO_PATH, format="audio/mp3")  # Play the static audio file

    # Transcribe the audio
    with st.spinner("Transcribing... Please wait."):
        transcription = transcribe_audio(STATIC_AUDIO_PATH)

    # Display the transcription
    st.subheader("Transcription:")
    st.write(transcription)
else:
    st.error(f"Audio file '{STATIC_AUDIO_PATH}' not found. Please place the file in the project folder.")

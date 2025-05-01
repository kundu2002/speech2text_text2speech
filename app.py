import streamlit as st
import whisper
import pyttsx3
import numpy as np
import os

# Try to import sounddevice, but handle the case where it might fail in cloud environments
try:
    import sounddevice as sd
    _has_sounddevice = True
except Exception as e:
    st.sidebar.error(f"Note: Audio recording hardware not available. Text-to-speech will still work.")
    _has_sounddevice = False

# Page configuration
st.set_page_config(page_title="Speech Utility App", page_icon="🎙️")

# Cache the Whisper model to load it only once
@st.cache_resource
def load_whisper_model():
    """Load Whisper model with caching to improve performance."""
    st.info("Loading Whisper model...")
    return whisper.load_model("tiny")

# Initialize text-to-speech engine
@st.cache_resource
def init_tts_engine():
    """Initialize text-to-speech engine with caching."""
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    return engine

def record_audio(duration=5, samplerate=16000):
    """Record audio from the microphone."""
    if not _has_sounddevice:
        # If we're in a cloud environment without audio hardware, provide mock audio
        st.warning("⚠️ Running in cloud environment - recording is simulated")
        st.info("In cloud environments like Streamlit Cloud, microphone access is not available.")
        st.info("Please use the text-to-speech feature instead, or run this app locally.")
        
        # Return a short silence with a bit of noise to simulate audio
        return np.random.normal(0, 0.01, size=int(samplerate * duration))
    
    try:
        st.info("🎤 Recording... Speak now!")
        audio_data = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
        sd.wait()
        st.success("✅ Recording complete!")
        return np.squeeze(audio_data)
    except Exception as e:
        st.error(f"Error recording audio: {e}")
        st.info("If you're running in a cloud environment, microphone access may not be available.")
        # Return mock audio data so the app can continue
        return np.random.normal(0, 0.01, size=int(samplerate * duration))

def transcribe_audio(model, audio):
    """Transcribe recorded audio using Whisper model."""
    if audio is None:
        st.warning("No audio recorded. Please try again.")
        return ""
    
    try:
        st.info("⏳ Transcribing...")
        # Check if this is likely mock audio (very quiet)
        if np.abs(audio).mean() < 0.02:
            # In cloud environments, we'll simulate a transcription of silent audio
            st.warning("Simulated transcription in cloud environment")
            return "This is simulated text because audio recording is not available in cloud environments."
        
        result = model.transcribe(audio)
        text = result["text"].strip()
        st.write(f"📝 Transcribed Text: {text}")
        return text
    except Exception as e:
        st.error(f"Error transcribing audio: {e}")
        return ""

def speak_text(engine, text):
    """Convert text to speech."""
    if not text:
        st.warning("No text to speak. Please enter some text.")
        return
    
    try:
        st.info("🔊 Speaking...")
        engine.say(text)
        engine.runAndWait()
        st.success("Speech completed!")
    except Exception as e:
        st.error(f"Error speaking text: {e}")
        st.info("Note: If running in cloud environment, audio playback may not be available.")

def main():
    # Initialize session state
    if 'whisper_model' not in st.session_state:
        st.session_state.whisper_model = load_whisper_model()
    
    if 'tts_engine' not in st.session_state:
        st.session_state.tts_engine = init_tts_engine()

    # App title and description
    st.title("🎙️ Speech Utility App")
    
    # Environment detection message
    in_cloud = os.environ.get('STREAMLIT_SHARING', '') == '1' or os.environ.get('IS_STREAMLIT_CLOUD', '') == '1' or not _has_sounddevice
    if in_cloud:
        st.info("ℹ️ Running in cloud environment - audio recording features will use simulation mode.")

    # Main app functionality
    tab1, tab2, tab3 = st.tabs(["Speak-to-Text", "Text-to-Speech", "Speak & Repeat"])

    with tab1:
        st.header("Speech Transcription")
        # Use a unique key for the button to reset state
        if st.button("🎤 Start Recording", key="record_transcribe"):
            # Reset any previous transcription state
            st.session_state.transcribed_text = ""
            
            # Record audio
            audio = record_audio()
            
            # Transcribe and store result
            if audio is not None:
                st.session_state.transcribed_text = transcribe_audio(st.session_state.whisper_model, audio)

    with tab2:
        st.header("Text-to-Speech")
        # Text input with key to maintain state
        user_text = st.text_area("Enter text to speak:", key="tts_input")
        
        if st.button("🔊 Speak Text", key="speak_text"):
            # Speak the current text in the text area
            speak_text(st.session_state.tts_engine, user_text)

    with tab3:
        st.header("Record and Repeat")
        if st.button("🎤 Record and Repeat", key="record_repeat"):
            # Reset previous state
            st.session_state.repeated_text = ""
            
            # Record audio
            audio = record_audio()
            
            # Transcribe
            if audio is not None:
                transcribed_text = transcribe_audio(st.session_state.whisper_model, audio)
                
                # Speak the transcribed text
                if transcribed_text:
                    st.info("🔄 Now repeating your speech...")
                    speak_text(st.session_state.tts_engine, transcribed_text)

    # Footer
    st.markdown("---")
    
if __name__ == "__main__":
    main()
import streamlit as st
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import make_chunks
from io import BytesIO

# Dictionary of supported languages with their codes
SUPPORTED_LANGUAGES = {
    'Arabic': 'ar', 'Armenian': 'hy', 'Azerbaijani': 'az',
    'Belarusian': 'be', 'Bosnian': 'bs', 'Bulgarian': 'bg', 'Catalan': 'ca',
    'Chinese (Simplified)': 'zh-CN', 'Chinese (Traditional)': 'zh-TW',
    'Croatian': 'hr', 'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl',
    'English': 'en', 'Estonian': 'et', 'Finnish': 'fi', 'French': 'fr',
    'Galician': 'gl', 'German': 'de', 'Greek': 'el', 'Hebrew': 'he',
    'Hindi': 'hi', 'Hungarian': 'hu', 'Icelandic': 'is', 'Indonesian': 'id',
    'Italian': 'it', 'Japanese': 'ja', 'Kannada': 'kn', 'Korean': 'ko',
    'Latvian': 'lv', 'Lithuanian': 'lt', 'Macedonian': 'mk', 'Malay': 'ms',
    'Marathi': 'mr', 'Norwegian': 'no', 'Persian': 'fa', 'Polish': 'pl',
    'Portuguese': 'pt', 'Romanian': 'ro', 'Russian': 'ru', 'Serbian': 'sr',
    'Slovak': 'sk', 'Slovenian': 'sl', 'Spanish': 'es', 'Swahili': 'sw',
    'Swedish': 'sv', 'Tagalog': 'tl', 'Tamil': 'ta', 'Thai': 'th',
    'Turkish': 'tr', 'Ukrainian': 'uk', 'Urdu': 'ur', 'Vietnamese': 'vi'
}

class AudioTranscriberApp:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def convert_audio_to_text(self, audio_file, selected_language):
        """
        Convert audio file to text.
        """
        try:
            st.write(f"Converting {audio_file.name} to text...")
            
            # Convert uploaded file to AudioSegment, handling different formats
            if audio_file.type == "audio/mpeg":
                audio = AudioSegment.from_mp3(audio_file)
            elif audio_file.type == "audio/x-wav":
                audio = AudioSegment.from_wav(audio_file)
            elif audio_file.type == "audio/mp4":
                audio = AudioSegment.from_file(audio_file, "m4a")
            else:
                st.error("Unsupported file format!")
                return None

            # Create chunks for processing
            chunk_length_ms = 60000  # 60 seconds
            chunks = make_chunks(audio, chunk_length_ms)
            
            full_text = []
            progress_bar = st.progress(0)
            
            for i, chunk in enumerate(chunks):
                chunk_wav = BytesIO()
                chunk.export(chunk_wav, format="wav")
                chunk_wav.seek(0)
                
                with sr.AudioFile(chunk_wav) as source:
                    audio_data = self.recognizer.record(source)
                    try:
                        text = self.recognizer.recognize_google(audio_data, language=selected_language)
                        full_text.append(text)
                        st.write(f"✓ Successfully processed chunk {i+1}/{len(chunks)}")
                    except sr.UnknownValueError:
                        st.warning(f"⚠️ Could not understand audio in chunk {i+1}")
                    except sr.RequestError as e:
                        st.error(f"❌ API error in chunk {i+1}: {e}")
                
                progress_bar.progress((i + 1) / len(chunks))
            
            return ' '.join(full_text) if full_text else None
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            return None

    def process_audio_file(self, file, selected_language):
        """
        Processes an uploaded audio file and saves the transcribed text.
        """
        text = self.convert_audio_to_text(file, selected_language)
        
        if text:
            output_file_path = f"./{file.name}.txt"
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            st.success("✅ Transcription completed successfully!")
            
            with open(output_file_path, "r", encoding='utf-8') as f:
                st.download_button(
                    label="📥 Download Transcribed Text",
                    data=f,
                    file_name=f"{file.name}.txt",
                    mime="text/plain"
                )
            
            #st.subheader("Preview:")
            st.markdown("### Preview:")
            st.text_area("Transcribed Text", text, height=200)

        else:
            st.error("❌ Failed to convert audio to text.")


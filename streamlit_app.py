import streamlit as st
from transcriber import AudioTranscriberApp, SUPPORTED_LANGUAGES
import tempfile
from youtube_audio import S3Client, YouTubeDownloader
from io import BytesIO
from youtube_audio2 import YouTubeDownloader, S3Uploader
#from audio_transcriber import AudioTranscriberApp, SUPPORTED_LANGUAGES
import boto3


# Initialize S3 client
def initialize_s3():
    return boto3.client(
        's3',
        aws_access_key_id=st.secrets["aws_access_key_id"],
        aws_secret_access_key=st.secrets["aws_secret_access_key"]
    )
    
def render_home():
    st.title("🎉 Welcome to the Multi-Tool Application!")
    st.write("""
    This app provides multiple tools, including an audio-to-text converter.
    Select a tool from the sidebar to get started.
    """)

def render_audio_transcriber():
    st.title("🎙️ Multi-language Audio to Text Converter")
    
    # Language selection
    selected_language_name = st.selectbox(
        "Select Audio Language",
        options=sorted(SUPPORTED_LANGUAGES.keys())
    )
    selected_language = SUPPORTED_LANGUAGES[selected_language_name]
    
    # File upload
    uploaded_file = st.file_uploader("Upload an audio file", type=["mp3"]) #, "wav", "m4a"])
    
    if uploaded_file is not None:
        st.write(f"📁 Uploaded file: {uploaded_file.name}")
        
        st.write(f"🔄 Convert to Text . . .")
        transcriber = AudioTranscriberApp()
        transcriber.process_audio_file(uploaded_file, selected_language)
        
       # if st.button("🔄 Convert to Text"):
       #     transcriber = AudioTranscriberApp()
       #     transcriber.process_audio_file(uploaded_file, selected_language)

def render_youtube_text():
    st.title("YouTube Audio Downloader and S3 Uploader")
    st.write("Enter a YouTube URL to download the audio and upload it to an S3 bucket.")

    # Inputs for YouTube URL and S3 Bucket
    youtube_url = st.text_input("YouTube URL:")
    bucket_name = st.text_input("S3 Bucket Name:", value="erman-demo-1")

    if st.button("Download and Upload"):
        if youtube_url and bucket_name:
            try:
                with st.spinner("Processing..."):
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Initialize downloader and S3 client
                        downloader = YouTubeDownloader(temp_dir, cookie_path="cookies.txt")
                        s3_client = S3Client(
                            aws_access_key_id=st.secrets["aws_access_key_id"],
                            aws_secret_access_key=st.secrets["aws_secret_access_key"]
                        )

                        # Step 1: Download the YouTube audio
                        title, audio_path = downloader.download_audio(youtube_url)
                        st.success(f"Downloaded audio: {title}")

                        # Step 2: Upload to S3
                        s3_audio_key = f"audio/{title}.mp3"
                        s3_url = s3_client.upload_file(audio_path, bucket_name, s3_audio_key)
                        st.success("Uploaded to S3 successfully!")
                        st.write(f"S3 URL: {s3_url}")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter both a YouTube URL and an S3 bucket name.")

def render_youtube_text2():
    st.title("YouTube Audio to Text Converter")
    st.write("Download YouTube audio, upload to S3, and transcribe the audio to text.")

    # Input fields
    youtube_url = st.text_input("YouTube URL:")
    bucket_name = st.text_input("S3 Bucket Name:", value="erman-demo-1")
    selected_language = st.selectbox("Select Transcription Language:", SUPPORTED_LANGUAGES.keys())

    if st.button("Process Audio"):
        if youtube_url and bucket_name:
            try:
                with st.spinner("Processing..."):
                    # Temporary directory for processing
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Step 1: Download YouTube audio
                        downloader = YouTubeDownloader(temp_dir)
                        title, audio_path = downloader.download_audio(youtube_url)
                        st.success(f"Downloaded audio: {title}")

                        # Step 2: Upload to S3
                        s3_audio_key = f"audio/{title}.mp3"
                        uploader = S3Uploader(bucket_name, initialize_s3())
                        s3_url = uploader.upload(audio_path, s3_audio_key)
                        st.success("Uploaded to S3 successfully!")
                        st.write(f"S3 URL: {s3_url}")

                        # Step 3: Retrieve audio from S3
                        s3 = initialize_s3()
                        obj = s3.get_object(Bucket=bucket_name, Key=s3_audio_key)
                        audio_file = BytesIO(obj['Body'].read())
                        audio_file.name = f"{title}.mp3"  # Simulate uploaded file
                        audio_file.type = "audio/mpeg"  # Add MIME type manually


                        # Step 4: Transcribe audio
                        transcriber = AudioTranscriberApp()
                        transcription = transcriber.convert_audio_to_text(
                            audio_file, SUPPORTED_LANGUAGES[selected_language]
                        )

                        if transcription:
                            st.success("Transcription completed successfully!")
                            st.text_area("Transcribed Text", transcription, height=200)
                            st.download_button(
                                label="📥 Download Transcribed Text",
                                data=transcription,
                                file_name=f"{title}.txt",
                                mime="text/plain"
                            )
                        else:
                            st.error("❌ Failed to transcribe audio.")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please provide both a YouTube URL and an S3 bucket name.")

def main():
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Go to", ["Home", "Audio Transcriber","Youtube to Text","Youtube to Text2"])
    
    if app_mode == "Home":
        render_home()
    elif app_mode == "Audio Transcriber":
        render_audio_transcriber()
    elif app_mode == "Youtube to Text":
        render_youtube_text()
    elif app_mode == "Youtube to Text2":
        render_youtube_text2()

if __name__ == "__main__":
    main()

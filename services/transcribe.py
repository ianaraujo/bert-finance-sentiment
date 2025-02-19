import os
import tempfile

from transformers import pipeline
from pytube import YouTube

class YouTubeTranscriptionService:
    def __init__(self, model_name: str = "openai/whisper-small", device: str = "cpu"):
        # Convert device string to an integer: 0 for GPU ("cuda"), -1 for CPU
        device_index = 0 if device.lower() == "cuda" else -1
        self.transcriber = pipeline(
            "automatic-speech-recognition", 
            model=model_name, 
            device=device_index
        )

    def transcribe(self, youtube_url: str) -> str:
        yt = YouTube(youtube_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        if not audio_stream:
            raise ValueError("No audio stream found for the given YouTube URL")
        
        # Create a temporary file to store the downloaded audio.
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_audio_file:
            temp_filename = temp_audio_file.name

        try:
            # Download the audio stream to the temporary file.
            audio_stream.download(
                output_path=os.path.dirname(temp_filename),
                filename=os.path.basename(temp_filename)
            )
            
            # Run the transcription. The pipeline accepts the file path directly.
            # We specify the language ("pt" for Portuguese) as part of the kwargs.
            result = self.transcriber(temp_filename, language="pt")
            transcription_text = result.get("text", "")
        finally:
            # Clean up the temporary file.
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
        
        return transcription_text

# Example usage:
if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=lX8V7KMbvOk"
    
    # Use device="cpu" or device="cuda". For CPU, the pipeline should get device index -1.
    service = YouTubeTranscriptionService(model_name="openai/whisper-small", device="cpu")
    transcript = service.transcribe(url)
    
    print("Transcription:", transcript)

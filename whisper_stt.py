import whisper
import numpy as np
import logging

class WhisperSTT:
    def __init__(self):
        self.model = whisper.load_model("base")
        logging.info("Whisper model loaded")

    async def transcribe(self, audio_frame):
        # Convert LiveKit audio frame to numpy array
        audio_data = np.frombuffer(audio_frame.data, dtype=np.int16)
        audio_data = audio_data.astype(np.float32) / 32768.0  # Normalize
        
        result = self.model.transcribe(audio_data, language="en")
        return result["text"].strip()
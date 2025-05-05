from gtts import gTTS
import os
import io
from livekit.agents import AudioFrame

class TTSHandler:
    async def say(self, text, session):
        tts = gTTS(text=text, lang="en")
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        # Convert to raw audio (simplified - use proper audio decoding)
        raw_audio = mp3_fp.read()
        frame = AudioFrame(
            data=raw_audio,
            sample_rate=24000,
            num_channels=1,
            samples_per_channel=len(raw_audio)//2
        )
        await session.audio.write_frame(frame)
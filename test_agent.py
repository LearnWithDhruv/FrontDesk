import asyncio
from livekit import rtc

async def test_agent():
    try:
        # 1. Initialize connection
        url = "wss://frontdesk-gy402rup.livekit.cloud"
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDYxNzcxMjMsImlzcyI6IkFQSVBwcE5kSnJNUmFOUCIsIm5iZiI6MTc0NjE3NjIyMywic3ViIjoibmV3IiwidmlkZW8iOnsiY2FuUHVibGlzaCI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwicm9vbSI6Im5ldyIsInJvb21Kb2luIjp0cnVlfX0.kI5dPbvvPAVe58ijQ9i4hClbQqT1Z6H5YPY-gh1L-9U"
        room = rtc.Room()
        await room.connect(url, token)
        print("Successfully connected to room:", room.name)

        # 2. Configure audio source with proper parameters
        sample_rate = 44100  # From your PyAudio output
        num_channels = 2     # From your PyAudio output
        audio_source = rtc.AudioSource(sample_rate, num_channels)
        
        # 3. Create and publish audio track
        track = rtc.LocalAudioTrack.create_audio_track(
            "mic", 
            audio_source  # Only pass the source here
        )
        publication = await room.local_participant.publish_track(track)
        print("Microphone published with config:")
        print(f"- Sample rate: {sample_rate}Hz")
        print(f"- Channels: {num_channels}")

        # 4. Event handlers
        @room.on("track_published")
        def on_track_published(publication, participant):
            print(f"New track published by {participant.identity}")

        @room.on("track_subscribed")
        def on_track_subscribed(track, publication, participant):
            print(f"Subscribed to {participant.identity}'s {track.kind} track")

        # 5. Keep connection alive
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        print("Error:", str(e))
    finally:
        await room.disconnect()

if __name__ == "__main__":
    asyncio.run(test_agent())
# test_client.py
import asyncio
from livekit import rtc

async def join_room():
    room = rtc.Room()
    await room.connect(
        "wss://frontdesk-gy402rup.livekit.cloud",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDYxNzcxMjMsImlzcyI6IkFQSVBwcE5kSnJNUmFOUCIsIm5iZiI6MTc0NjE3NjIyMywic3ViIjoibmV3IiwidmlkZW8iOnsiY2FuUHVibGlzaCI6dHJ1ZSwiY2FuUHVibGlzaERhdGEiOnRydWUsImNhblN1YnNjcmliZSI6dHJ1ZSwicm9vbSI6Im5ldyIsInJvb21Kb2luIjp0cnVlfX0.kI5dPbvvPAVe58ijQ9i4hClbQqT1Z6H5YPY-gh1L-9U"
    )
    
    @room.on("track_subscribed")
    def on_track(track, *_):
        if track.kind == rtc.TrackKind.KIND_AUDIO:
            print("Agent audio track received!")
    
    await room.local_participant.publish_microphone()
    print("Connected to room. Speak and you should hear responses.")

asyncio.run(join_room())
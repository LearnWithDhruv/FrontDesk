import os
import asyncio
import numpy as np
from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit import rtc
from llm import query_llm
from escalation import escalate_question
import logging
import whisper
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("salon_agent")
load_dotenv()

class SalonAgent(Agent):
    def __init__(self):
        super().__init__(
            publish_subscribed=True,
            audio=True,
            video=False
        )
        self._should_disconnect = asyncio.Event()
        self._audio_task = None
        
        self.sample_rate = 16000
        self.chunk_duration = 1.5
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        self.audio_buffer = bytearray()
        
        try:
            logger.info("Loading Whisper model...")
            self.stt_model = whisper.load_model("base")
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    async def on_connect(self, session: AgentSession):
        logger.info(f"Connected to room: {session.room.name}")
        
        participants = session.room.participants
        logger.debug(f"Current participants ({len(participants)}):")
        for p in participants:
            logger.debug(f" - {p.identity} (tracks: {len(p.tracks)})")
        
        if session.audio.track:
            logger.info(f"Subscribed to audio track: {session.audio.track.sid}")
            logger.debug(f"Audio track details: "
                         f"codec={session.audio.track.codec}, "
                         f"sample_rate={session.audio.track.sample_rate}, "
                         f"num_channels={session.audio.track.num_channels}")
        else:
            logger.error("No audio track subscribed! Client must publish audio")
        
        await session.audio.say("Hello! I'm Bella from Bella's Salon. How can I help you today?")
        logger.info("Initial greeting sent")
        
        self._audio_task = asyncio.create_task(self._audio_processing_loop(session))

    async def _audio_processing_loop(self, session: AgentSession):
        logger.info("Starting audio processing loop")
        frames_received = 0
        bytes_received = 0
        
        try:
            while not self._should_disconnect.is_set():
                try:
                    frame = await asyncio.wait_for(
                        session.audio.read(),
                        timeout=0.5
                    )
                    
                    if frame is None:
                        continue
                        
                    frames_received += 1
                    
                    if isinstance(frame, rtc.AudioFrame):
                        bytes_received += len(frame.data)
                        
                        if frames_received % 10 == 0:
                            logger.debug(
                                f"Audio frame #{frames_received}: "
                                f"{len(frame.data)} bytes, "
                                f"{frame.sample_rate}Hz, "
                                f"{frame.num_channels} channels, "
                                f"{frame.samples_per_channel} samples"
                            )
                        
                        if frame.sample_rate != self.sample_rate or frame.num_channels > 1:
                            frame = frame.remix_and_resample(
                                self.sample_rate,
                                1
                            )
                            logger.debug("Audio frame resampled to 16kHz mono")
                        
                        raw_samples = np.frombuffer(frame.data, dtype=np.int16)
                        self.audio_buffer.extend(raw_samples.tobytes())
                        
                        while len(self.audio_buffer) >= self.chunk_size * 2:
                            chunk = self.audio_buffer[:self.chunk_size * 2]
                            self.audio_buffer = self.audio_buffer[self.chunk_size * 2:]
                            
                            samples = np.frombuffer(chunk, dtype=np.int16)
                            await self._process_audio_chunk(samples, session)

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Audio processing error: {str(e)}")
                    break
                    
        except Exception as e:
            logger.error(f"Audio loop crashed: {str(e)}")
        finally:
            logger.info(f"Audio processing ended. Received {frames_received} frames ({bytes_received} bytes)")

    async def _process_audio_chunk(self, samples: np.ndarray, session: AgentSession):
        try:
            logger.debug(f"Processing audio chunk ({len(samples)} samples)")
            audio_float = samples.astype(np.float32) / 32768.0
            start_time = datetime.now()
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: self.stt_model.transcribe(
                    audio_float,
                    language="en",
                    fp16=False
                )
            )
            transcribe_time = (datetime.now() - start_time).total_seconds()
            text = result["text"].strip()
            if text:
                logger.info(f"Transcription ({transcribe_time:.2f}s): '{text}'")
                start_time = datetime.now()
                response = await self._generate_response(text, session.room.name)
                process_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"Generated response ({process_time:.2f}s): '{response}'")
                await session.audio.say(response)
            else:
                logger.debug("No speech detected in audio chunk")
                
        except Exception as e:
            logger.error(f"Audio chunk processing failed: {str(e)}")

    async def _generate_response(self, question: str, caller_id: str) -> str:
        try:
            logger.info(f"Processing question: '{question}'")
            answer = await query_llm(question)
            
            if any(phrase in answer.lower() for phrase in ["i don't know", "check with", "supervisor"]):
                logger.info("Escalating to supervisor")
                request_id = escalate_question(question, caller_id)
                logger.info(f"Created help request ID: {request_id}")
                return "Let me check with my supervisor and get back to you."
            
            return answer
        except Exception as e:
            logger.error(f"Question processing failed: {str(e)}")
            escalate_question(question, caller_id)
            return "I'm having some trouble answering that. Let me connect you with someone who can help."

    async def on_disconnect(self):
        logger.info("Agent disconnecting...")
        self._should_disconnect.set()
        
        if self._audio_task:
            self._audio_task.cancel()
            try:
                await self._audio_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Error during audio task cancellation: {str(e)}")

async def entrypoint(ctx: JobContext):
    logger.info("Starting salon agent")
    try:
        host = os.getenv("LIVEKIT_URL").strip('"').replace("wss://", "")
        logger.debug(f"Connecting to LiveKit at {host}")
        
        await ctx.connect(
            host=host,
            api_key=os.getenv("LIVEKIT_API_KEY").strip('"'),
            api_secret=os.getenv("LIVEKIT_API_SECRET").strip('"'),
            timeout=15
        )
        logger.info("LiveKit connected successfully")
        
        agent = SalonAgent()
        session = AgentSession(agent=agent, room=ctx.room)
        await session.start()
        
        await agent._should_disconnect.wait()
        
    except Exception as e:
        logger.error(f"Agent failed: {str(e)}")
        raise
    finally:
        logger.info("Agent session ended")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))

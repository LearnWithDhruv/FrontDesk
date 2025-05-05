
# AI Customer Service (LiveAgent)

This repository appears to be an AI-powered voice assistant application, using technologies like:
- Whisper for speech-to-text
- TTS (text-to-speech)
- LLM for natural language understanding
- Firebase for backend integration
- Flask for the server
- LiveKit CLI for real-time communication

---

## Folder Structure

### `livekit-cli/`
Contains LiveKit CLI tools or scripts for real-time audio/video communication.

### `models/`
Contains saved models or model architecture-related files.

### `static/`
Holds static assets like images, CSS, or JavaScript files.

### `templates/`
HTML templates rendered by Flask.

### `venv/`
Python virtual environment.

---

## Main Files

### `.env`
Environment variables for Firebase, API keys, or secret configs.

### `agent.py`
Handles the logic of the AI agent (likely NLP-based dialogue management).

### `app.py`
Main Flask app entry point. Serves web routes, possibly includes API endpoints for STT, TTS, and LLM queries.

### `db.py`
Handles database operations (user sessions, messages, or logging).

### `escalation.py`
Handles escalation to a human agent if the bot fails to answer.

### `firebase_init.py`
Initializes Firebase admin SDK or services (auth, Firestore, etc.).

### `frontdesk-*.json`
Firebase service account credentials.

### `knowledge_base.json`
A static knowledge base file used by the LLM for querying responses.

### `llm.py`
Logic related to the LLM (e.g., OpenAI, LangChain, etc.), possibly for RAG (retrieval augmented generation).

### `requirements.txt`
Lists Python dependencies. Use `pip install -r requirements.txt` to install.

### `test_agent.py`
Unit or integration test for the `agent.py` module.

### `test_client.py`
Client-side tests (e.g., testing API endpoints or full conversation flows).

### `tts.py`
Text-to-speech system (possibly using TTS APIs like Google, ElevenLabs, or pyttsx3).

### `whisper_stt.py`
Speech-to-text using Whisper (OpenAI's STT model).

### `agent_debug.log`
Runtime logs or debug information from the agent.

### `tempCodeRunnerFile.py`
Temporary file created by VSCode during script execution.

---

## How to Run

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Run the backend agent
python agent.py start
```

---

## Notes
- Ensure your `.env` file contains all sensitive configs (Firebase credentials, API keys, Flask secret).
- Update paths in `firebase_init.py` and `llm.py` to point to correct credentials or endpoints.

---

## Potential Enhancements
- Add real-time UI with WebSockets
- Improve escalation via third-party CRM APIs
- Add multilingual STT/TTS support


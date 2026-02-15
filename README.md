# Salesvoice – Real-Time AI Sales Agent (LiveKit Edition)

Salesvoice is a **real-time, interruptible** AI voice sales assistant powered by **LiveKit Agents**.
It listens to users, understands sales intent, fetches product info from a mock catalog, and responds naturally with voice.

**Core Tech Stack:**
- **Real-Time Transport:** LiveKit (WebRTC)
- **Agent Framework:** LiveKit Agents (Python)
- **LLM:** Groq (Llama 3 70B via OpenAI plugin)
- **STT/TTS:** Deepgram
- **Frontend:** Next.js + LiveKit Components

## Features
- ⚡ **True Real-Time**: Low latency voice streaming.
- 🗣️ **Interruptible**: Speak over the agent to stop it instantly.
- 🛠️ **Tool Calling**: The Agent queries a product database and manages orders.
- 📊 **Visualizer**: Real-time audio visualization.

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 18+
- **LiveKit Cloud Account** (Sign up at [cloud.livekit.io](https://cloud.livekit.io))
- Groq API Key
- Deepgram API Key

### 1. Configuration
Create a `.env` file in the root directory:
```ini
GROQ_API_KEY=your_groq_key
DEEPGRAM_API_KEY=your_deepgram_key
LIVEKIT_URL=your_livekit_url
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
```

### 2. Run the App
We have provided a script to start everything (Backend Token Server, Agent Worker, and Frontend).

```bash
# From salesvoice/ root
chmod +x run.sh
./run.sh
```

**Manual Start:**
1.  **Token Server**: `uvicorn backend.main:app --reload --port 8000`
2.  **Agent Worker**: `python backend/agent.py dev`
3.  **Frontend**: `cd frontend && npm run dev`

Open [http://localhost:3000](http://localhost:3000) to use the assistant.

## Architecture
Browser (LiveKit SDK) <--> LiveKit Cloud <--> Python Agent (Worker)
                                      |
                                  Groq LLM
                                      |
                                  Deepgram STT/TTS

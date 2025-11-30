---
title: VoiceBot
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Advanced Voice Bot Interview Assistant

A modern, production-ready voice-to-voice interview bot built with React frontend and Flask backend.

## 🎯 Features

- **Voice Input/Output**: Complete voice-to-voice pipeline
- **Real-Time Communication**: WebSocket support for streaming
- **Multi-Provider AI**: Groq and OpenAI with automatic fallback
- **Session Management**: Persistent conversations
- **Caching**: Intelligent caching to reduce costs
- **Rate Limiting**: Protection against abuse
- **Modern UI**: Responsive React frontend
- **Production-Ready**: Comprehensive logging, error handling, monitoring

## 🏗️ Architecture

- **Frontend**: React 18 + Vite (Port 3000)
- **Backend**: Flask 3.0 + Flask-SocketIO (Port 5000)
- **AI Services**: Whisper (STT), Groq/OpenAI (LLM), YourTTS (TTS)
- **Storage**: Redis (optional) or in-memory cache
- **WebSocket**: Real-time bidirectional communication

## 🚀 Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
python run.py
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Docs: http://localhost:5000/api/health

## 📁 Project Structure

```
.
├── backend/           # Flask API
│   ├── app/
│   │   ├── routes/   # API endpoints
│   │   ├── services/ # Business logic
│   │   ├── utils/    # Utilities
│   │   └── middleware/ # Middleware
│   └── run.py
├── frontend/         # React app
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── context/
│   └── package.json
└── README.md
```

## 🔧 Configuration

### Backend (.env)
- `GROQ_API_KEY` - Required
- `OPENAI_API_KEY` - Optional (for fallback)
- `REDIS_ENABLED` - Enable Redis caching
- `RATE_LIMIT_PER_MINUTE` - Rate limiting

### Frontend (.env)
- `VITE_API_BASE_URL` - Backend API URL
- `VITE_WS_URL` - WebSocket URL

## 📝 API Endpoints

- `POST /api/session` - Create session
- `POST /api/transcribe` - Audio to text
- `POST /api/chat` - Generate response
- `POST /api/tts` - Text to speech
- `POST /api/process` - Complete pipeline
- `GET /api/conversation/:id` - Get history
- `DELETE /api/conversation/:id` - Clear history

## 🎨 Features

### Frontend
- WebRTC audio recording
- Real-time conversation display
- Audio playback
- Session persistence
- Error handling
- Responsive design

### Backend
- RESTful API
- WebSocket support
- Multi-provider LLM
- Intelligent caching
- Rate limiting
- Comprehensive logging
- Error recovery

## 🚢 Deployment

### Backend
- Railway, Render, AWS, or Hugging Face Spaces
- Set environment variables
- Install dependencies
- Run `python run.py`

### Frontend
- Vercel, Netlify, or static hosting
- Set environment variables
- Build: `npm run build`
- Deploy `dist/` folder

## 📊 Monitoring

- Health check: `GET /api/health`
- Logs: `backend/logs/`
- Metrics: Tracked in ProcessingMetrics

## 🔒 Security

- API keys in environment variables
- Rate limiting per IP/session
- Input validation
- CORS configuration
- Session security

## 📄 License

Built for 100x AI Agent Team Interview Assessment

---

**Built by**: Balamurugan Nithyanantham

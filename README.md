# 🎙️ Echoes — Hear the World in Familiar Voices

> *What if your morning news was read by your father? What if a bedtime story was narrated by your grandmother? Echoes makes it possible.*

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green)
![XTTS](https://img.shields.io/badge/XTTS-v2-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🌟 What is Echoes?

Echoes is a personal voice reader that converts any text into audio — spoken in the voice of someone you love.

Upload a short voice sample of anyone. Paste any text. Echoes generates the audio in that exact voice using state-of-the-art voice cloning.

**This is not a generic TTS tool. This is personal.**

---

## ✨ Features

- 🎤 **Voice cloning** — clone any voice from just 6 seconds of audio
- 🧹 **Smart audio preprocessing** — automatic noise reduction, normalisation, silence trimming
- 📊 **Audio quality scoring** — rates reference audio 0–100 before cloning
- 🌍 **Multilingual** — 17 languages including English, Hindi, French, Spanish, Arabic, Japanese
- 🔌 **REST API** — full FastAPI backend callable from any software
- 📁 **Multi-format support** — WAV, MP3, M4A, OGG, FLAC, AAC (auto-converted)
- 🔒 **API key security** — protected endpoints
- ☁️ **Cloud ready** — Google Colab, RunPod, Vast.ai

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Voice Cloning Engine | XTTS v2 (Coqui TTS) |
| API Framework | FastAPI |
| Audio Processing | librosa, noisereduce, soundfile |
| Format Conversion | ffmpeg |
| Cloud Deployment | Google Colab + ngrok |
| Language | Python 3.12 |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- NVIDIA GPU (recommended — CPU works but is slow)
- ffmpeg installed

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/echoes.git
cd echoes
```

### 2. Install Dependencies

```bash
# System dependency
apt-get install ffmpeg

# Python packages
pip install -r requirements.txt
```

### 3. Set Environment Variables

```bash
cp .env.example .env
# Edit .env and add your API key
```

### 4. Run the API

```bash
python app.py
```

API is now live at `http://localhost:8000`

### 5. Clone a Voice

```python
import requests

BASE_URL = "http://localhost:8000"
headers  = {"X-API-Key": "your-api-key"}

with open("voice_sample.m4a", "rb") as audio:
    response = requests.post(
        f"{BASE_URL}/clone",
        headers=headers,
        data={
            "text": "Hello, this is Echoes speaking in your voice.",
            "language": "en"
        },
        files={"reference_audio": audio}
    )

with open("output.wav", "wb") as f:
    f.write(response.content)

print("✓ Audio generated successfully")
```

---

## 📡 API Reference

### Base URL
```
http://localhost:8000
```

### Authentication
All endpoints (except `/`) require an API key passed as a header:
```
X-API-Key: your-secret-key
```

### Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | No | API info and available endpoints |
| GET | `/health` | Yes | Server status and GPU info |
| POST | `/check-audio` | Yes | Score reference audio quality |
| POST | `/clone` | Yes | Clone voice and generate speech |

---

### GET `/health`

```http
GET /health
X-API-Key: your-secret-key
```

**Response:**
```json
{
  "status": "running",
  "model": "XTTS_v2",
  "device": "cuda",
  "gpu_available": true
}
```

---

### POST `/check-audio`

Score your reference audio quality before cloning.

```http
POST /check-audio
X-API-Key: your-secret-key
Content-Type: multipart/form-data

reference_audio: [audio file]
```

**Response:**
```json
{
  "quality_score": 92.6,
  "rating": "Excellent",
  "duration_seconds": 24.47,
  "recommendation": "Use this audio"
}
```

---

### POST `/clone`

Clone a voice and generate speech.

```http
POST /clone
X-API-Key: your-secret-key
Content-Type: multipart/form-data

text: "Text you want spoken"
language: "en"
reference_audio: [audio file]
```

**Response:** WAV audio file (audio/wav)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| text | string | Yes | Text to be spoken (max 5000 chars) |
| language | string | No | Language code (default: en) |
| reference_audio | file | Yes | Voice sample (min 6 seconds) |

---

## 🌍 Supported Languages

| Code | Language | Code | Language |
|------|----------|------|----------|
| `en` | English | `fr` | French |
| `de` | German | `es` | Spanish |
| `it` | Italian | `pt` | Portuguese |
| `zh` | Chinese | `ja` | Japanese |
| `ko` | Korean | `hi` | Hindi |
| `ar` | Arabic | `ru` | Russian |
| `nl` | Dutch | `pl` | Polish |
| `tr` | Turkish | `cs` | Czech |
| `hu` | Hungarian | | |

---

## 📊 Audio Quality Guide

| Score | Rating | Expected Result |
|-------|--------|-----------------|
| 80–100 | Excellent | Best cloning quality |
| 60–80 | Good | Recommended minimum |
| 40–60 | Fair | Acceptable results |
| 0–40 | Poor | Use a better recording |

**Tips for best clone quality:**
- ✅ Minimum **6 seconds** of audio (30 seconds = much better)
- ✅ Record in a **quiet room** — no background noise or echo
- ✅ **Natural speech** — varied pitch clones better than monotone
- ✅ Use **WAV, MP3 or M4A** format
- ❌ No background music, reverb, or overlapping voices

---

## 🏗️ Project Structure

```
echoes/
│
├── app.py                    # FastAPI application — all endpoints
├── preprocessor.py           # Audio cleaning pipeline
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
│
├── notebooks/
│   └── echoes_colab.ipynb    # Full Colab deployment notebook
│
├── uploads/                  # Temporary reference audio (gitignored)
├── outputs/                  # Generated audio files (gitignored)
│
└── README.md
```

---

## ☁️ Deployment

### Google Colab (Development)

Open `notebooks/echoes_colab.ipynb` with GPU runtime:

1. `Runtime → Change runtime type → GPU (T4)`
2. Run all cells top to bottom
3. Your public API URL appears after Cell 7

### RunPod (Production — Always On)

```bash
# On your RunPod instance
git clone https://github.com/prince4115/Echoes---A-Voice-Clonning-API.git
cd echoes
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Environment Variables

```bash
# .env
API_KEY=your-secret-key-here
```

---

## 🔮 Roadmap

- [ ] Web interface — drag and drop voice + paste text
- [ ] Mobile app — iOS and Android
- [ ] Document upload — PDF, EPUB, DOCX support
- [ ] Voice library — save and name multiple voice profiles
- [ ] Emotion control — adjust tone and expression
- [ ] Agentic layer — fetch and read any URL autonomously
- [ ] Offline mode — fully local processing

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 💡 The Idea Behind Echoes

Most voice cloning tools are built for content creators or enterprises.

Echoes is built for people.

For the child who wants to hear a bedtime story in their parent's voice.
For the person who lost someone and wants to feel close again.
For anyone who finds comfort in a familiar voice.

Technology doesn't have to feel cold. It can feel like home.

---

*Built with XTTS v2 · FastAPI · Python*

**If this resonated with you — give it a ⭐ and share it with someone who needs to hear a familiar voice.**

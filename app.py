from fastapi import FastAPI, UploadFile, File, Form, Security, HTTPException
from fastapi.security import APIKeyHeader
from fastapi.responses import FileResponse
from preprocessor import clean_audio, score_audio_quality, convert_to_wav
import subprocess
import librosa
import torch
import os

from dotenv import load_dotenv
load_dotenv()

# ── Directories ────────────────────────────────────────────────
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# ── Config ─────────────────────────────────────────────────────
API_KEY = os.getenv("API_KEY", "change-this-secret-key")

# ── Load XTTS v2 Model ─────────────────────────────────────────
from TTS.api import TTS

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading XTTS v2 model on {device}...")
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
print("✓ Model ready")

# ── FastAPI App ────────────────────────────────────────────────
app = FastAPI(
    title="Echoes — Voice Cloning API",
    description="Clone any voice from a short audio sample and generate speech.",
    version="1.0.0"
)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_key(key: str = Security(api_key_header)):
    if key is None or key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key. Pass it as X-API-Key header."
        )
    return key

# ── Root ───────────────────────────────────────────────────────
@app.get("/", tags=["Status"])
def root():
    return {
        "name": "Echoes Voice Cloning API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "GET /health",
            "check_audio": "POST /check-audio",
            "clone": "POST /clone"
        }
    }

# ── Health ─────────────────────────────────────────────────────
@app.get("/health", tags=["Status"])
def health(api_key: str = Security(verify_key)):
    return {
        "status": "running",
        "model": "XTTS_v2",
        "device": device,
        "gpu_available": torch.cuda.is_available()
    }

# ── Check Audio Quality ────────────────────────────────────────
@app.post("/check-audio", tags=["Utilities"])
async def check_audio(
    reference_audio: UploadFile = File(...),
    api_key: str = Security(verify_key)
):
    """
    Score reference audio quality before cloning.
    Score above 60 = good. Above 80 = excellent.
    """
    ref_path = f"uploads/check_{reference_audio.filename}"
    with open(ref_path, "wb") as f:
        f.write(await reference_audio.read())

    # Convert if needed before scoring
    if not ref_path.lower().endswith(".wav"):
        wav_path = ref_path.rsplit(".", 1)[0] + ".wav"
        convert_to_wav(ref_path, wav_path)
        ref_path = wav_path

    score    = score_audio_quality(ref_path)
    audio, sr = librosa.load(ref_path)
    duration = librosa.get_duration(y=audio, sr=sr)
    rating   = (
        "Poor" if score < 40 else
        "Fair" if score < 60 else
        "Good" if score < 80 else
        "Excellent"
    )

    return {
        "quality_score": score,
        "rating": rating,
        "duration_seconds": round(duration, 2),
        "recommendation": (
            "Use this audio" if score >= 60
            else "Try a cleaner, longer recording for better results"
        )
    }

# ── Clone Voice ────────────────────────────────────────────────
@app.post("/clone", tags=["Voice Cloning"])
async def clone_voice(
    text: str = Form(..., description="Text to speak in the cloned voice"),
    language: str = Form(
        default="en",
        description="Language code: en, fr, de, es, it, pt, zh, ja, ko, hi, ar, ru, nl, pl, tr, cs, hu"
    ),
    reference_audio: UploadFile = File(
        ...,
        description="Audio sample of target voice — minimum 6 seconds"
    ),
    api_key: str = Security(verify_key)
):
    """
    Clone a voice and generate speech.

    - Accepts: WAV, MP3, M4A, OGG, FLAC, AAC
    - Minimum 6 seconds reference audio recommended
    - Returns: WAV audio file
    """

    # Validate text
    if len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Text too long. Maximum 5000 characters.")

    # Validate file extension
    filename = reference_audio.filename.lower()
    allowed  = [".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac"]
    if not any(filename.endswith(ext) for ext in allowed):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {allowed}"
        )

    # Save uploaded file
    ref_path    = f"uploads/ref_{reference_audio.filename}"
    clean_path  = f"uploads/clean_{reference_audio.filename}.wav"
    output_path = f"outputs/cloned_{reference_audio.filename.split('.')[0]}.wav"

    with open(ref_path, "wb") as f:
        f.write(await reference_audio.read())

    # Convert to WAV if needed
    if not ref_path.lower().endswith(".wav"):
        converted = ref_path.rsplit(".", 1)[0] + ".wav"
        convert_to_wav(ref_path, converted)
        ref_path  = converted

    # Check quality
    quality = score_audio_quality(ref_path)
    if quality < 20:
        raise HTTPException(
            status_code=400,
            detail=f"Audio quality too low ({quality}/100). Please use a cleaner recording."
        )

    # Clean and preprocess
    clean_audio(ref_path, clean_path)

    # Generate cloned speech
    tts.tts_to_file(
        text=text,
        speaker_wav=clean_path,
        language=language,
        file_path=output_path
    )

    return FileResponse(
        output_path,
        media_type="audio/wav",
        filename="echoes_output.wav",
        headers={"X-Quality-Score": str(quality)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

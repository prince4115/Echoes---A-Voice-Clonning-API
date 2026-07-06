"""
Echoes — Example Usage
======================
Shows how to call the Echoes API from Python.
"""

import requests
import os
from pathlib import Path


BASE_URL = "http://localhost:8000"
API_KEY  = os.getenv("API_KEY", "your-api-key-here")
HEADERS  = {"X-API-Key": API_KEY}


def health_check():
    """Check if the API is running."""
    res = requests.get(f"{BASE_URL}/health", headers=HEADERS)
    print("Health:", res.json())


def check_audio_quality(audio_file: str):
    """Score reference audio quality before cloning."""
    with open(audio_file, "rb") as f:
        res = requests.post(
            f"{BASE_URL}/check-audio",
            headers=HEADERS,
            files={"reference_audio": f},
            timeout=30
        )
    data = res.json()
    print(f"Quality Score : {data['quality_score']}/100")
    print(f"Rating        : {data['rating']}")
    print(f"Duration      : {data['duration_seconds']}s")
    print(f"Recommendation: {data['recommendation']}")
    return data["quality_score"]


def clone_voice(text: str, audio_file: str, language: str = "en", output: str = "output.wav"):
    """Clone a voice and generate speech."""
    print(f"\nCloning voice from: {audio_file}")
    print(f"Text: {text[:80]}...")

    with open(audio_file, "rb") as f:
        res = requests.post(
            f"{BASE_URL}/clone",
            headers=HEADERS,
            data={"text": text, "language": language},
            files={"reference_audio": f},
            timeout=120
        )

    if res.status_code == 200:
        with open(output, "wb") as f:
            f.write(res.content)
        print(f"✓ Audio saved: {output}")
        return output
    else:
        print(f"✗ Error: {res.json()}")
        return None


if __name__ == "__main__":
    # 1. Check server
    health_check()

    # 2. Check audio quality
    # Replace with your actual voice sample path
    VOICE_SAMPLE = "voice_samples/my_voice.m4a"

    if Path(VOICE_SAMPLE).exists():
        score = check_audio_quality(VOICE_SAMPLE)

        if score >= 40:
            # 3. Clone voice
            clone_voice(
                text="Hello, this is Echoes speaking in a cloned voice. Technology can feel like home.",
                audio_file=VOICE_SAMPLE,
                language="en",
                output="outputs/example_output.wav"
            )
    else:
        print(f"\nNote: Add a voice sample at {VOICE_SAMPLE} to test cloning.")
        print("Any WAV, MP3, M4A, OGG, or FLAC file works.")

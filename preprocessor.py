import librosa
import soundfile as sf
import noisereduce as nr
import numpy as np
import subprocess


def convert_to_wav(input_path: str, output_path: str, target_sr: int = 22050) -> str:
    """
    Convert any audio format (M4A, MP3, OGG, FLAC, AAC) to WAV using ffmpeg.

    Args:
        input_path:  Path to input audio file
        output_path: Path to save converted WAV
        target_sr:   Target sample rate (default: 22050 — what XTTS v2 expects)

    Returns:
        output_path on success
    """
    subprocess.run([
        "ffmpeg",
        "-i", input_path,
        "-ar", str(target_sr),
        "-ac", "1",           # mono channel
        "-y",                 # overwrite if exists
        output_path
    ], capture_output=True)
    return output_path


def clean_audio(input_path: str, output_path: str, target_sr: int = 22050) -> str:
    """
    Full audio cleaning pipeline:
    1. Convert to WAV if not already
    2. Reduce background noise
    3. Normalise volume
    4. Trim silence from start and end

    Args:
        input_path:  Path to input audio file
        output_path: Path to save cleaned WAV
        target_sr:   Target sample rate

    Returns:
        output_path on success
    """
    # Convert if not WAV
    if not input_path.lower().endswith(".wav"):
        converted = input_path.rsplit(".", 1)[0] + "_converted.wav"
        convert_to_wav(input_path, converted, target_sr)
        input_path = converted

    # Load audio
    audio, sr = librosa.load(input_path, sr=target_sr)

    # Noise reduction
    reduced = nr.reduce_noise(y=audio, sr=sr)

    # Normalise volume
    normalised = librosa.util.normalize(reduced)

    # Trim silence
    trimmed, _ = librosa.effects.trim(normalised, top_db=20)

    # Save
    sf.write(output_path, trimmed, target_sr)
    return output_path


def score_audio_quality(audio_path: str) -> float:
    """
    Score reference audio quality from 0 to 100.

    Scoring criteria:
    - Duration (longer = better, up to 30s)
    - Signal-to-noise ratio (cleaner = better)

    Ratings:
    - 0–40:   Poor      — try a better recording
    - 40–60:  Fair      — acceptable results
    - 60–80:  Good      — recommended
    - 80–100: Excellent — best results

    Args:
        audio_path: Path to audio file to score

    Returns:
        Quality score 0–100 (float)
    """
    audio, sr   = librosa.load(audio_path)
    duration    = librosa.get_duration(y=audio, sr=sr)
    signal_pwr  = np.mean(audio ** 2)
    noise_floor = np.percentile(np.abs(audio), 10)
    snr         = 10 * np.log10(signal_pwr / (noise_floor ** 2 + 1e-10))
    score       = min(100, (duration / 30) * 40 + min(snr, 30) * 2)
    return round(float(score), 1)

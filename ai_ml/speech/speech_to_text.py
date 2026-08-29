import os
from pathlib import Path

from dotenv import load_dotenv

try:
    from sarvamai import SarvamAI
except ImportError:  # pragma: no cover
    SarvamAI = None


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


def get_sarvam_client():
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("SARVAM_API_KEY is missing from .env")
    if SarvamAI is None:
        raise ModuleNotFoundError("sarvamai is not installed.")
    return SarvamAI(api_subscription_key=api_key)


def transcribe_audio(audio_path, model="saaras:v3", mode="transcribe"):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    client = get_sarvam_client()
    with open(audio_path, "rb") as audio_file:
        response = client.speech_to_text.transcribe(file=audio_file, model=model, mode=mode)

    transcript = getattr(response, "transcript", None)
    if transcript is None and hasattr(response, "result"):
        transcript = response.result
    if transcript is None:
        transcript = str(response)

    return {
        "text": transcript,
        "model": model,
        "mode": mode,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python speech_to_text.py <audio_file_path>")
    else:
        result = transcribe_audio(sys.argv[1])
        print(result["text"])
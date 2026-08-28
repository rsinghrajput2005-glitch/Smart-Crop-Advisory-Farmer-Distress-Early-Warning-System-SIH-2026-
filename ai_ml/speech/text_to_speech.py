import os
from pathlib import Path

from dotenv import load_dotenv

from ai_ml.speech.language_config import get_sarvam_language_code

try:
    from sarvamai import SarvamAI
    from sarvamai.play import save
except ImportError:  # pragma: no cover
    SarvamAI = None
    save = None


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


def get_sarvam_client():
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("SARVAM_API_KEY is missing from .env")
    if SarvamAI is None:
        raise ModuleNotFoundError("sarvamai is not installed.")
    return SarvamAI(api_subscription_key=api_key)


def text_to_speech(text, language="English", output_path=None, speaker="shubh", model="bulbul:v3"):
    if not text or not str(text).strip():
        raise ValueError("Text is empty. Nothing to convert to speech.")

    client = get_sarvam_client()
    language_code = get_sarvam_language_code(language)

    if output_path is None:
        output_dir = Path(__file__).resolve().parent / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "advisory_audio.wav"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        response = client.text_to_speech.convert(
            text=text,
            language_code=language_code,
            model=model,
            speaker=speaker,
        )
    except TypeError:
        response = client.text_to_speech.convert(
            text=text,
            language_code=language_code,
            model=model,
        )
    except Exception:
        response = client.text_to_speech.convert(
            text=text,
            language_code=language_code,
            model=model,
        )

    if save is None:
        raise ModuleNotFoundError("sarvamai.play.save is not available.")

    save(response, str(output_path))
    return str(output_path)


if __name__ == "__main__":
    result = text_to_speech("This is a sample advisory in English.", language="English")
    print(result)
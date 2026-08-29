import tempfile
import traceback
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ai_ml.speech.text_to_speech import text_to_speech
from ai_ml.speech.language_config import is_supported_language, get_language_name

router = APIRouter(prefix="/tts", tags=["Text to Speech"])


class SpeakRequest(BaseModel):
    text: str
    language: str = "English"


@router.post("/speak")
def speak(req: SpeakRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty.")

    language = get_language_name(req.language) if is_supported_language(req.language) else "English"

    try:
        tmp_dir = Path(tempfile.gettempdir()) / "krishimitra_tts"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        output_path = tmp_dir / f"tts_{abs(hash((req.text, language)))}.wav"

        audio_path = text_to_speech(
            text=req.text,
            language=language,
            output_path=output_path,
        )
    except ValueError as e:
        # e.g. missing SARVAM_API_KEY
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")

    return FileResponse(
        path=audio_path,
        media_type="audio/wav",
        filename="advisory_audio.wav",
    )
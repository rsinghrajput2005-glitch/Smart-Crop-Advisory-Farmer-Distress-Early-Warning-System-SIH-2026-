import os

try:
    from faster_whisper import WhisperModel
    _FASTER_WHISPER_AVAILABLE = True
    _FASTER_WHISPER_IMPORT_ERROR = None
except Exception as _err:
    WhisperModel = None
    _FASTER_WHISPER_AVAILABLE = False
    _FASTER_WHISPER_IMPORT_ERROR = _err


class SpeechToText:
    def __init__(self,
                 model_size:str = "small",
                 device:str="cpu",
                 compute_type:str="int8"):
        if not _FASTER_WHISPER_AVAILABLE:
            raise ImportError(
                "faster_whisper is not installed. Install it with `pip install faster-whisper` "
                f"or run this code in an environment that has it available. Original error: {_FASTER_WHISPER_IMPORT_ERROR}"
            )

        print("Loading Whisper model...")

        self.model = WhisperModel(
            model_size,
            device = device,
            compute_type = compute_type

        )

        print("Whisper model loaded successfully.")

    def transcribe(self, audio_path: str, language: str | None = None) -> dict:
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=5
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
        ).strip()

        return {
            "text": text,
            "language": info.language,
            "language_probability": round(
                info.language_probability, 4
            )
        }


class MockSpeechToText:
    def transcribe(self, audio_path: str, language: str | None = None) -> dict:
        language = language or "en"
        return {
            "text": f"[mock transcription for {os.path.basename(audio_path)}]",
            "language": language,
            "language_probability": 1.0,
        }

_stt = None


def _get_stt() -> SpeechToText:
    global _stt
    if _stt is not None:
        return _stt

    # If the caller requests a mock (via env var), return the mock implementation.
    use_mock = os.getenv("SPEECH_USE_MOCK", "").lower() in ("1", "true", "yes")
    if use_mock:
        _stt = MockSpeechToText()
        return _stt

    _stt = SpeechToText()
    return _stt


def speech_to_text(
        audio_path: str,
        language: str | None = None
) -> dict:
    stt = _get_stt()
    return stt.transcribe(
        audio_path,
        language
    )
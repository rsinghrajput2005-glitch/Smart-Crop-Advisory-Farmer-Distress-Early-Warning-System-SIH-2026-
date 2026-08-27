from pathlib import Path


class TextToSpeech:
    """
    Multilingual Text-to-Speech interface.

    The actual TTS model will be plugged into this class.
    """

    def __init__(self):
        self.model = None

    def generate(
        self,
        text: str,
        language: str,
        output_path: str
    ) -> str:

        if not text.strip():
            raise ValueError(
                "Text cannot be empty."
            )

        output_file = Path(output_path)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        raise NotImplementedError(
            "Multilingual TTS model is not configured yet."
        )


tts = TextToSpeech()


def text_to_speech(
    text: str,
    language: str,
    output_path: str
) -> str:

    return tts.generate(
        text,
        language,
        output_path
    )
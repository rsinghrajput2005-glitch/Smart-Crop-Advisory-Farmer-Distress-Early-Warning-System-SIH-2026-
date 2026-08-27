import os
import sys


sys.path.insert(0, os.path.dirname(__file__))

from speech_to_text import speech_to_text


AUDIO_FILE = os.path.join(os.path.dirname(__file__), "sample2_odia.wav")


def main():
    print("\nStarting Speech-to-Text test...\n")

    # Support a test flag to use the mock STT implementation without
    # installing heavy dependencies: `python test_speech.py --mock`
    if "--mock" in sys.argv:
        os.environ["SPEECH_USE_MOCK"] = "1"

    try:
        result = speech_to_text(AUDIO_FILE)
    except Exception as exc:
        print("Error during transcription:", exc)
        return

    if not isinstance(result, dict):
        print("Unexpected result from speech_to_text:", result)
        return

    print("Transcription:")
    print(result.get("text", ""))

    print("\nDetected language:")
    print(result.get("language", ""))

    print("\nLanguage probability:")
    print(result.get("language_probability", ""))


if __name__ == "__main__":
    main()
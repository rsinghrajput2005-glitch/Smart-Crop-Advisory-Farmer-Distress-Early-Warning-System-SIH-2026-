SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "or": "Odia",
    "as": "Assamese",
    "mr": "Marathi",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "ur": "Urdu",
}


def is_supported_language(language: str) -> bool:
    return language in SUPPORTED_LANGUAGES


def get_language_name(language: str) -> str:
    return SUPPORTED_LANGUAGES.get(language, "Unknown")
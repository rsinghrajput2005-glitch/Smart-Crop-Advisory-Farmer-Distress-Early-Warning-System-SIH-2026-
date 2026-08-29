SUPPORTED_LANGUAGES = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Bengali": "bn-IN",
    "Odia": "od-IN",
    "Assamese": "as-IN",
    "Marathi": "mr-IN",
    "Gujarati": "gu-IN",
    "Punjabi": "pa-IN",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Kannada": "kn-IN",
    "Malayalam": "ml-IN",
    "Urdu": "ur-IN",
}

LANGUAGE_ALIASES = {
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
    "english": "English",
    "hindi": "Hindi",
    "marathi": "Marathi",
    "odia": "Odia",
}


def normalize_language(language: str) -> str:
    if language is None:
        return "English"
    value = str(language).strip()
    if not value:
        return "English"
    return LANGUAGE_ALIASES.get(value.lower(), value)


def is_supported_language(language: str) -> bool:
    normalized = normalize_language(language)
    return normalized in SUPPORTED_LANGUAGES


def get_language_name(language: str) -> str:
    normalized = normalize_language(language)
    return normalized if normalized in SUPPORTED_LANGUAGES else "English"


def get_sarvam_language_code(language: str) -> str:
    normalized = normalize_language(language)
    return SUPPORTED_LANGUAGES.get(normalized, "en-IN")
import re
from langdetect import detect

def detect_language(text: str) -> str:
    # Japanese characters (Hiragana, Katakana, Kanji)
    if re.search(r'[\u3040-\u30ff\u4e00-\u9faf]', text):
        return "Japanese"

    # Arabic
    if re.search(r'[\u0600-\u06FF]', text):
        return "Arabic"

    # Chinese
    if re.search(r'[\u4e00-\u9fff]', text):
        return "Chinese"

    try:
        lang_code = detect(text)
    except:
        return "English"

    mapping = {
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "de": "German",
        "hi": "Hindi"
    }

    return mapping.get(lang_code, "English")

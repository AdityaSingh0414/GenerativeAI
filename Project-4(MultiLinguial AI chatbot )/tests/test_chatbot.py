from services.language_detector import detect_language
from services.translator import translate_text

def test_language_detection():
    assert detect_language("Hola, ¿cómo estás?") == "es"

def test_translation_to_selected_language():
    result = translate_text("Hello, how are you?", source="en", target="fr")
    assert "bonjour" in result.lower() or "comment" in result.lower()
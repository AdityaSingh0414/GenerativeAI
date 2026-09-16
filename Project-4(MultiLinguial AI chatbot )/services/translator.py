from deep_translator import GoogleTranslator

def translate_text(text: str, source: str, target: str) -> str:
    """
    Translates text between any two supported languages.
    source= 'auto' can be used if the source language is unknown.
    """
    if source == target:
        return text
    try:
        return GoogleTranslator(source =source , target=target).translate(text)
    except Exception as e :
        print(f"Translation error: {e}")
        return text
    
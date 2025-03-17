from happytransformer import TTSettings

def enhance_text(text, happy_tt):
    """Enhance text for better grammar and clarity."""
    args = TTSettings(num_beams=5, min_length=2, max_length=100)
    enhanced_text = happy_tt.generate_text(f"grammar: {text}", args)
    return enhanced_text.text.strip()

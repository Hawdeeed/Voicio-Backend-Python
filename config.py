import whisper
from happytransformer import HappyTextToText

def setup_models():
    """Load Whisper and T5-based text enhancement models."""
    print("Loading Whisper model...")
    model = whisper.load_model("base")
    print("Whisper model loaded successfully.")

    print("Loading T5-based text enhancement model...")
    happy_tt = HappyTextToText("T5", "vennify/t5-base-grammar-correction")
    print("T5 model loaded successfully.")

    return model, happy_tt

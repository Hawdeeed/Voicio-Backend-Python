import whisper
from pydub import AudioSegment

def transcribe_audio(audio_path, model):
    """Convert audio to 16kHz mono and transcribe it."""
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(audio_path, format="wav")

    result = model.transcribe(audio_path, language="en")
    return result["text"]

import tempfile
import edge_tts

async def text_to_speech(text):
    """Convert enhanced text into speech."""
    try:
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        output_path = temp_audio.name
        temp_audio.close()

        tts = edge_tts.Communicate(text, voice="en-US-JennyNeural")
        await tts.save(output_path)

        return output_path
    except Exception as e:
        print(f"Error in text-to-speech: {str(e)}")
        return str(e)

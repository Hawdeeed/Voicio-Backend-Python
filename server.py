from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import whisper
import os
import asyncio
import tempfile
import time
from pydub import AudioSegment
import edge_tts
from happytransformer import HappyTextToText, TTSettings

app = Flask(__name__)
CORS(app)

# Load Whisper model (small for better accuracy)
print("Loading Whisper model...")
model = whisper.load_model("base")
print("Whisper model loaded successfully.")

# Load T5-based text enhancement model
print("Loading T5-based text enhancement model...")
happy_tt = HappyTextToText("T5", "vennify/t5-base-grammar-correction")
print("T5 model loaded successfully.")

def enhance_text(text):
    """Enhance text for better grammar and clarity."""
    start_time = time.time()
    args = TTSettings(num_beams=5, min_length=2, max_length=100)
    enhanced_text = happy_tt.generate_text(f"grammar: {text}", args)
    end_time = time.time()
    
    print(f"Text enhancement completed in {end_time - start_time:.2f} seconds.")
    return enhanced_text.text.strip()

async def text_to_speech(text):
    """Convert enhanced text into speech."""
    start_time = time.time()
    try:
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        output_path = temp_audio.name
        temp_audio.close()

        # Generate speech
        tts = edge_tts.Communicate(text, voice="en-US-JennyNeural")
        await tts.save(output_path)

        end_time = time.time()
        print(f"Text-to-Speech completed in {end_time - start_time:.2f} seconds.")
        return output_path
    except Exception as e:
        print(f"Error in text-to-speech: {str(e)}")
        return str(e)

@app.route("/process_audio", methods=["POST"])
def process_audio():
    total_start_time = time.time()

    if "file" not in request.files:
        print("No file provided in request.")
        return jsonify({"error": "No file provided"}), 400

    audio_file = request.files["file"]
    audio_path = "uploaded_audio.wav"
    audio_file.save(audio_path)
    print("Audio file received and saved.")

    # Convert audio to 16kHz mono (required for Whisper)
    start_time = time.time()
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_frame_rate(16000).set_channels(1)
    audio.export(audio_path, format="wav")
    end_time = time.time()
    print(f"Audio preprocessing completed in {end_time - start_time:.2f} seconds.")

    try:
        # Transcribe audio using Whisper with forced English language
        start_time = time.time()
        result = model.transcribe(audio_path, language="en")  # 👈 Forces English transcription
        transcribed_text = result["text"]
        end_time = time.time()
        print(f"Speech-to-Text (Whisper) completed in {end_time - start_time:.2f} seconds.")

        # Enhance text using T5 model
        enhanced_text = enhance_text(transcribed_text)

        # Convert enhanced text to speech
        output_audio_path = asyncio.run(text_to_speech(enhanced_text))

        # Clean up original audio file
        os.remove(audio_path)
        print("Original audio file deleted.")

        total_end_time = time.time()
        print(f"Total processing time: {total_end_time - total_start_time:.2f} seconds.")

        return jsonify({
            "transcribed_text": transcribed_text,
            "enhanced_text": enhanced_text,
            "audio_url": f"http://localhost:5000/get_audio/{os.path.basename(output_audio_path)}"
        })
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/get_audio/<filename>", methods=["GET"])
def get_audio(filename):
    """Serve the generated speech audio file."""
    file_path = os.path.join(tempfile.gettempdir(), filename)
    if os.path.exists(file_path):
        print(f"Serving generated audio file: {filename}")
        return send_file(file_path, as_attachment=True, mimetype="audio/mp3")
    else:
        print("Requested audio file not found.")
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)

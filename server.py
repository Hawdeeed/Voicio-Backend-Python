from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import asyncio
import tempfile

from transcribe import transcribe_audio
from enhance import enhance_text
from tts import text_to_speech
from config import setup_models

app = Flask(__name__)
CORS(app)

# Load models
model, happy_tt = setup_models()

@app.route("/process_audio", methods=["POST"])
def process_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    audio_file = request.files["file"]
    audio_path = "uploaded_audio.wav"
    audio_file.save(audio_path)

    try:
        transcribed_text = transcribe_audio(audio_path, model)
        enhanced_text = enhance_text(transcribed_text, happy_tt)
        output_audio_path = asyncio.run(text_to_speech(enhanced_text))

        os.remove(audio_path)

        return jsonify({
            "transcribed_text": transcribed_text,
            "enhanced_text": enhanced_text,
            "audio_url": f"http://localhost:5000/get_audio/{os.path.basename(output_audio_path)}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_audio/<filename>", methods=["GET"])
def get_audio(filename):
    file_path = os.path.join(tempfile.gettempdir(), filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, mimetype="audio/mp3")
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)

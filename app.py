from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from gtts import gTTS
import os
from googletrans import Translator
from werkzeug.utils import secure_filename
import uuid
import asyncio
import assemblyai as aai
from dotenv import load_dotenv

load_dotenv()
ASSEMBLYAI_API_KEY = os.getenv('ASSEMBLYAI_API_KEY')

# Initialize Flask app
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "/tmp/uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Allowed audio formats
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize translator and speech recognizer
translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '' or not allowed_file(audio_file.filename):
        return jsonify({'error': 'Invalid or unsupported file format'}), 400

    filename = secure_filename(audio_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
    audio_file.save(file_path)

    try:
        aai.settings.api_key = ASSEMBLYAI_API_KEY
        transcriber = aai.Transcriber()
        

        # Transcribe the audio file
        transcript = transcriber.transcribe(file_path)

        # Assuming `transcript.text` contains the transcription
        transcription_text = transcript.text if hasattr(transcript, 'text') else str(transcript)
        print(transcription_text)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        os.remove(file_path)

    return jsonify({'transcript': transcription_text})


@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    if 'text' not in data or 'target_language' not in data:
        return jsonify({'error': 'Missing text or target_language'}), 400

    text = data['text']
    target_language = data['target_language']

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        translated = loop.run_until_complete(translator.translate(text, dest=target_language))
        translated_text = translated.text
        tts = gTTS(translated_text, lang=target_language)
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        tts.save(audio_path)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'translated_text': translated_text, 'audio_url': f"/audio/{audio_filename}"})

@app.route('/audio/<filename>')
def audio(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run()

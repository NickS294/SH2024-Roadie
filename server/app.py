import openai
import os
import requests
import uuid
from flask import Flask, request, jsonify, send_file, render_template
from dotenv import load_dotenv
import os

load_dotenv()
ELEVENLABS_API_KEY= os.environ['ELEVENLABS_API_KEY']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY
ELEVENLABS_VOICE_STABILITY = 0.5
ELEVENLABS_VOICE_SIMILARITY = 0.75
ELEVENLABS_VOICE_NAME = "Bella" 

from utils import update_profile_info, create_user_profile, get_next_profile_question, profile_info, whisper_client, elevenlabs_client, generate_flowchart
from elevenlabs import VoiceSettings
profile= None
flow_chart= None
ELEVENLABS_ALL_VOICES = []

app = Flask(__name__)

def transcribe_audio(filename: str) -> str:
    with open(filename, "rb") as audio_file:
        transcript = whisper_client.audio.transcriptions.create(
            model="whisper-1", 
            file= audio_file,
            language="en"
        )
    return transcript.text.strip()

def generate_reply(conversation: list) -> str:
    if update_profile_info(conversation[-1], conversation[:-1]):
        print("Updated profile info:", {k: v for k, v in profile_info.items() if v is not None})
        if all(profile_info.values()):
            profile = create_user_profile(conversation)
            _= generate_flowchart(profile)
            
            return "Thank you for sharing. Based on what you've told me, here's a summary of your profile"
        
    return get_next_profile_question(conversation)

def generate_audio(text: str, output_path: str = "") -> str:
    audio_stream = elevenlabs_client.text_to_speech.convert(
            voice_id="VBFC8kJbxuX1jslJGh3q", #Paola Voice
            model_id="eleven_turbo_v2",
            text=text,
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.8,
            )
        )
        
    audio_data = b''.join(list(audio_stream))
    with open(output_path, "wb") as output:
        output.write(audio_data)
    return output_path

@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html', voice=ELEVENLABS_VOICE_NAME)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Transcribe the given audio to text using Whisper."""
    if 'file' not in request.files:
        return 'No file found', 400
    file = request.files['file']
    recording_file = f"{uuid.uuid4()}.wav"
    recording_path = f"uploads/{recording_file}"
    os.makedirs(os.path.dirname(recording_path), exist_ok=True)
    file.save(recording_path)
    transcription = transcribe_audio(recording_path)
    return jsonify({'text': transcription})

@app.route('/greeting', methods=['POST'])
def greeting():
    """Greet user"""
    greeting= "Hello! I'm here! I would love to learn about you. Could you start by telling me your name?"
    greeting_file = f"{uuid.uuid4()}.mp3"
    greeting_path = f"outputs/{greeting_file}"
    os.makedirs(os.path.dirname(greeting_path), exist_ok=True)
    generate_audio(greeting, output_path=greeting_path)
    return jsonify({'text': greeting, 'audio': f"/listen/{greeting_file}"})

@app.route('/ask', methods=['POST'])
def ask():
    """Generate a ChatGPT response from the given conversation, then convert it to audio using ElevenLabs."""
    conversation = request.get_json(force=True).get("conversation", "")
    reply = generate_reply(conversation)
    reply_file = f"{uuid.uuid4()}.mp3"
    reply_path = f"outputs/{reply_file}"
    os.makedirs(os.path.dirname(reply_path), exist_ok=True)
    print(reply)
    generate_audio(reply, output_path=reply_path)
    return jsonify({'text': reply, 'audio': f"/listen/{reply_file}"})

@app.route('/listen/<filename>')
def listen(filename):
    """Return the audio file located at the given filename."""
    return send_file(f"outputs/{filename}", mimetype="audio/mp3", as_attachment=False)

if __name__ == '__main__':
    app.run()

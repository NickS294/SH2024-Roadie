import io

from flask import Flask, render_template, request
from utils import whisper_client

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/transcribe", methods=["POST"])
    def transcribe():
        file = request.files["audio"]
        buffer = io.BytesIO(file.read())
        buffer.name = "audio.webm"

        transcript = whisper_client.audio.transcriptions.create(
            model="whisper-1",
            file=buffer,
            language="en"
        )

        return {"output": transcript.text}

    return app
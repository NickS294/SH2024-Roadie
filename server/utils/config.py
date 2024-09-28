import os
from dotenv import load_dotenv
import speech_recognition as sr
import whisper
import openai
from elevenlabs import ElevenLabs
import queue
import threading
import pygame

load_dotenv()

client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])
elevenlabs_client = ElevenLabs(api_key=os.environ['ELEVENLABS_API_KEY'])

whisper_model = whisper.load_model("medium")

recognizer = sr.Recognizer()
recognizer.energy_threshold = 1800
recognizer.dynamic_energy_threshold = True

pygame.mixer.init()

transcription_queue = queue.Queue()
speech_queue = queue.Queue()

profile_info = {q: None for q in ["name", "goals", "interests", "recent_challenge"]}

is_speaking = threading.Event()
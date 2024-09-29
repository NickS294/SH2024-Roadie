import os
import openai
import elevenlabs
import asyncio
import pygame
import anthropic

from dotenv import load_dotenv
load_dotenv()

client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])
whisper_client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])
anthropic_client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
elevenlabs_client =elevenlabs.ElevenLabs(api_key=os.environ['ELEVENLABS_API_KEY'])

pygame.mixer.init()

# Queues and Events
transcription_queue = asyncio.Queue()
speech_queue = asyncio.Queue()
audio_queue = asyncio.Queue()

# Events
is_speaking = asyncio.Event()
transcription_result = asyncio.Event()

# Profile information
profile_info = {q: None for q in ["name", "goals", "interests", "challenge"]}

# Global variables for conversation state
conversation_task = None
speech_task = None
profile_result = None
flowchart_result = None
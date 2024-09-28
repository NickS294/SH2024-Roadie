import speech_recognition as sr
import numpy as np
import pygame
import io
from elevenlabs import VoiceSettings
from .config import recognizer, whisper_model, elevenlabs_client, transcription_queue, speech_queue, is_speaking

def listen_and_transcribe():
    with sr.Microphone(sample_rate=16000) as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening...")
        
        while True:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                np_audio = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
                np_audio = np_audio.astype(np.float32) / np.iinfo(np.int16).max
                
                result = whisper_model.transcribe(np_audio, fp16=False, language='en')
                text = result['text'].strip()
                
                if text:
                    print(f"Transcribed: '{text}'")
                    transcription_queue.put(text)
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                print(f"An error occurred in transcription: {e}")

def speak(text):
    is_speaking.set()
    print(f"AI: {text}")
    try:
        audio_stream = elevenlabs_client.text_to_speech.convert(
            voice_id="VBFC8kJbxuX1jslJGh3q", #Paola Voice
            model_id="eleven_turbo_v2",
            text=text,
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.8,
            ),
        )
        
        audio_data = b''.join(list(audio_stream))
        
        audio_stream = io.BytesIO(audio_data)
        pygame.mixer.music.load(audio_stream)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Error in speech synthesis: {e}")
    finally:
        is_speaking.clear()

def speech_worker():
    while True:
        text = speech_queue.get()
        speak(text)
        speech_queue.task_done()
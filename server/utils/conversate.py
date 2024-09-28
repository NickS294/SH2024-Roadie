"""
This file has all componets in a single script just in case.
"""
import speech_recognition as sr
import whisper
import numpy as np
import openai
import threading
import queue
import time
import pygame
import io
from elevenlabs import ElevenLabs, VoiceSettings
import os
from dotenv import load_dotenv
import json

load_dotenv()

client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])
elevenlabs_client = ElevenLabs(api_key=os.environ['ELEVENLABS_API_KEY'])

whisper_model = whisper.load_model("medium")

recognizer = sr.Recognizer()
recognizer.energy_threshold = 1500
recognizer.dynamic_energy_threshold = True

pygame.mixer.init()

transcription_queue = queue.Queue()
speech_queue = queue.Queue()

profile_questions = [
    "What is your name?",
    "What are your goals?",
    "The user's main interests or hobbies",
    "What's a recent challenge you've faced?"
]
profile_info = {q: None for q in ["name", "goals", "interests", "recent_challenge"]}

greeting_sent = False
profile_created = False
is_speaking = threading.Event()

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

def get_gpt_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in AI response: {e}")
        return "I'm sorry, I'm having trouble thinking right now. Can you please repeat that?"

def update_profile_info(user_input):
    function_description = {
        "name": "update_user_profile",
        "description": "Update user profile information based on their response",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"},
                        "meets_criteria": {"type": "boolean"}
                    },
                    "description": "The user's name"
                },
                "goals": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"},
                        "meets_criteria": {"type": "boolean"}
                    },
                    "description": "The user's goals"
                },
                "interests": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"},
                        "meets_criteria": {"type": "boolean"}
                    },
                    "description": "The user's main interests or hobbies"
                },
                "recent_challenge": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"},
                        "meets_criteria": {"type": "boolean"}
                    },
                    "description": "A recent challenge the user has faced"
                }
            }
        }
    }

    messages = [
        {"role": "system", "content": "You are an AI assistant tasked with extracting relevant user profile information from their response. For each piece of information, determine if it meets the criteria to be considered complete and valid."},
        {"role": "user", "content": f"User's response: {user_input}"}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            functions=[function_description],
            function_call={"name": "update_user_profile"}
        )

        function_response = response.choices[0].message.function_call
        if function_response:
            function_args = json.loads(function_response.arguments)
            
            updated = False
            for key, value in function_args.items():
                if value and value['meets_criteria'] and profile_info[key] is None:
                    profile_info[key] = value['value']
                    updated = True
            
            return updated
    except Exception as e:
        print(f"Error in update_profile_info: {e}")
    
    return False

def create_user_profile():
    profile_message = [
        {"role": "system", "content": "You are an AI assistant tasked with creating a comprehensive user profile based on the following information. Create a detailed and engaging summary of the user."},
        {"role": "user", "content": f"User information:\n" + "\n".join([f"{q}: {a}" for q, a in profile_info.items()])}
    ]
    return get_gpt_response(profile_message)

def get_next_profile_question(conversation_history):
    unanswered_questions = [q for q, a in profile_info.items() if a is None]
    if unanswered_questions:
        next_question = unanswered_questions[0]
        prompt_message = [
            {"role": "system", "content": "You are an AI assistant tasked with asking a specific question in a natural, conversational way. Consider the conversation history and formulate the question to flow naturally."},
            {"role": "user", "content": f"Conversation history: {conversation_history}\nQuestion to ask: {next_question}"}
        ]
        return get_gpt_response(prompt_message)
    return None

def manage_conversation():
    global greeting_sent, profile_created
    conversation_history = []
    last_user_speech_time = None
    last_ai_response_time = time.time()
    
    ai_response_delay = 4
    silence_prompt_interval = 30
    max_silence_prompts = 3
    extended_silence_threshold = 120
    initial_silence_threshold = 10
    
    silence_prompt_count = 0
    waiting_to_respond = False
    
    def ai_speak(text):
        nonlocal last_ai_response_time
        speech_queue.put(text)
        last_ai_response_time = time.time()
        conversation_history.append({"role": "assistant", "content": text})
        
    while True:
        current_time = time.time()
        
        if not greeting_sent:
            greeting = "Hello! I'm here! I would love to learn about you. Could you start by telling me your name?"
            ai_speak(greeting)
            greeting_sent = True
            continue
        
        user_spoke = False
        while not transcription_queue.empty():
            user_input = transcription_queue.get()
            print(f"User: {user_input}")
            conversation_history.append({"role": "user", "content": user_input})
            last_user_speech_time = current_time
            silence_prompt_count = 0
            user_spoke = True
            waiting_to_respond = True
            
            if update_profile_info(user_input):
                print("Updated profile info:", {k: v for k, v in profile_info.items() if v is not None})
                if all(profile_info.values()) and not profile_created:
                    profile = create_user_profile()
                    ai_speak(f"Thank you for sharing. Based on what you've told me, here's a summary of your profile: {profile}")
                    profile_created = True
                    waiting_to_respond = False
        
        if user_spoke:
            time.sleep(ai_response_delay)
            continue
        
        if is_speaking.is_set():
            time.sleep(0.1)
            continue
        
        time_since_user_spoke = current_time - last_user_speech_time if last_user_speech_time else float('inf')
        time_since_ai_spoke = current_time - last_ai_response_time
        
        if waiting_to_respond and time_since_user_spoke > ai_response_delay and time_since_ai_spoke > ai_response_delay:
            next_question = get_next_profile_question(conversation_history) or get_gpt_response(conversation_history)
            ai_speak(next_question)
            waiting_to_respond = False
        elif time_since_ai_spoke > silence_prompt_interval:
            if len(conversation_history) == 1 and time_since_ai_spoke > initial_silence_threshold:
                prompt = "Feel free to share anything about yourself or ask me any questions you might have."
            elif silence_prompt_count < max_silence_prompts:
                prompt = get_gpt_response(conversation_history + [{"role": "system", "content": "The user has been silent for a while. Generate a gentle, non-repetitive prompt or question."}])
                silence_prompt_count += 1
            elif time_since_ai_spoke > extended_silence_threshold:
                prompt = "I'm still here if you'd like to continue our conversation. Feel free to ask me anything."
                silence_prompt_count = 0
            
            ai_speak(prompt)
        
        time.sleep(0.1)

def main():
    print("Starting the AI assistant. Speak naturally!")
    
    threading.Thread(target=listen_and_transcribe, daemon=True).start()
    
    threading.Thread(target=speech_worker, daemon=True).start()
    
    threading.Thread(target=manage_conversation, daemon=True).start()
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()
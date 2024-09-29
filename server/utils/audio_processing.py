import asyncio
import io
from elevenlabs import VoiceSettings
from .config import elevenlabs_client, whisper_client, transcription_queue, speech_queue, is_speaking, audio_queue
import json

async def listen_and_transcribe():
    print("Listening...")
    audio_data = io.BytesIO()
    content_type = None
    
    while True:
        data = await audio_queue.get()
        if data is None:  # Signal to stop listening
            break
        if content_type is None:
            content_type, chunk = data
        else:
            _, chunk = data
        audio_data.write(chunk)
    
    audio_data.seek(0)
    
    try:
        result = await whisper_client.audio.transcriptions.create(
            model="whisper-1", 
            file=("audio_file", audio_data, content_type),
            language="en"
        )
        
        text = result.text.strip()
        
        if text:
            print(f"Transcribed: '{text}'")
            await transcription_queue.put(text)
    except Exception as e:
        print(f"An error occurred in transcription: {e}")
        await transcription_queue.put(None)

async def speak(text):
    is_speaking.set()
    print(f"AI: {text}")
    try:
        audio_stream = await asyncio.to_thread(
            elevenlabs_client.text_to_speech.convert,
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
        
        # Send the audio data to the client
        await speech_queue.put(json.dumps({"type": "audio", "content": audio_data.decode('latin1')}))
    except Exception as e:
        print(f"Error in speech synthesis: {e}")
    finally:
        is_speaking.clear()

async def speech_worker():
    while True:
        message = await speech_queue.get()
        message_data = json.loads(message)
        if message_data['type'] == 'speech':
            await speak(message_data['content'])
        elif message_data['type'] == 'audio':
            # This is already handled in the speak function
            pass
        elif message_data['type'] == 'end':
            # Send the end message to the client
            await speech_queue.put(message)
        speech_queue.task_done()
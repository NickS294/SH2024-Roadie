import os
from dotenv import load_dotenv
from elevenlabs import ElevenLabs, VoiceSettings
import asyncio
import io

__all__ = ['speak']

load_dotenv()
client = ElevenLabs(api_key=os.environ['ELEVENLABS_API_KEY'])

async def speak(text):
    try:
        audio_stream = await asyncio.to_thread(
            client.text_to_speech.convert,
            voice_id="21m00Tcm4TlvDq8ikWAM",
            model_id="eleven_turbo_v2",
            text=text,
            voice_settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=0.8,
            ),
        )
        
        audio_data = b''.join(list(audio_stream))
        
        await asyncio.to_thread(play_audio, audio_data)
    except Exception as e:
        print(f"Error in speech synthesis: {e}")

def play_audio(audio_data):
    from pydub import AudioSegment
    from pydub.playback import play
    
    audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
    play(audio_segment)

if __name__ == '__main__':
    asyncio.run(speak('Hello! I am your AI assistant. How can I help you today?'))
import speech_recognition as sr
import whisper
import numpy as np
import logging
import asyncio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

model = whisper.load_model("large")  # Load model once, outside the function

async def listen():
    r = sr.Recognizer()
    r.energy_threshold = 1000
    r.dynamic_energy_threshold = True
    
    with sr.Microphone(sample_rate=16000) as source:
        r.adjust_for_ambient_noise(source, duration=1)
        logging.info("Listening...")
        
        while True:
            try:
                audio = await asyncio.to_thread(r.listen, source, timeout=5, phrase_time_limit=10)
                np_audio = np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(np.float32) / 32768.0
                
                result = await asyncio.to_thread(model.transcribe, np_audio, fp16=False)
                text = result['text'].strip()
                
                if text:
                    logging.info(f"Transcribed: '{text}'")
                    yield text, True
                else:
                    yield "", False

            except sr.WaitTimeoutError:
                yield "", False
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                yield "", False

if __name__ == "__main__":
    async def main():
        async for text, is_final in listen():
            if text:
                print(f"Transcribed{'(Final)' if is_final else ''}: {text}")

    asyncio.run(main())
import os
import struct
import pyaudio
import pvporcupine
from dotenv import load_dotenv
import asyncio

__all__ = ['wait_for_wake_word']

load_dotenv()

class WakeWordDetector:
    def __init__(self, keyword_path):
        self.access_key = os.environ['PICOVOICE_ACCESS_KEY']
        self.keyword_path = keyword_path
        self.porcupine = None
        self.pa = None
        self.audio_stream = None

    async def initialize(self):
        self.porcupine = pvporcupine.create(
            access_key=self.access_key,
            keyword_paths=[self.keyword_path]
        )
        self.pa = pyaudio.PyAudio()
        self.audio_stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

    async def detect(self):
        try:
            while True:
                pcm = await asyncio.to_thread(
                    lambda: struct.unpack_from("h" * self.porcupine.frame_length,
                                               self.audio_stream.read(self.porcupine.frame_length))
                )
                keyword_index = await asyncio.to_thread(self.porcupine.process, pcm)
                if keyword_index >= 0:
                    return True
                await asyncio.sleep(0.01)  # Small delay to prevent CPU overuse
        finally:
            if self.audio_stream is not None:
                self.audio_stream.close()
            if self.pa is not None:
                self.pa.terminate()
            if self.porcupine is not None:
                self.porcupine.delete()

async def wait_for_wake_word(keyword_path):
    detector = WakeWordDetector(keyword_path)
    await detector.initialize()
    print("Waiting for wake word...")
    return await detector.detect()
import threading
import time
from utils import *

def main():
    print("Starting the AI assistant. Speak naturally!")
    
    threading.Thread(target=listen_and_transcribe, daemon=True).start()
    threading.Thread(target=speech_worker, daemon=True).start()
    threading.Thread(target=manage_conversation, daemon=True).start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()
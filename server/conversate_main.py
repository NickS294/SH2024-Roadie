import threading
import time
from utils import *

def main():
    print("Starting the AI assistant. Speak naturally!")
    
    threading.Thread(target=listen_and_transcribe, daemon=True).start()
    threading.Thread(target=speech_worker, daemon=True).start()

    profile = manage_conversation() 
    flowchart= generate_flowchart(profile)
    print(flowchart)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()
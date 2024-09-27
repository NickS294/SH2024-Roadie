import asyncio
from senses import *

async def main():
    print("Loading conversation history...")
    load_conversation()

    keyword_path = "./senses/Commence_en_linux_v3_0_0.ppn"

    while True:
        print("Waiting for wake word...")
        if await wait_for_wake_word(keyword_path):
            print("Wake word detected! Listening...")
            async for text, is_final in listen():
                if is_final and text:
                    print(f"You said: {text}")
                    response = await think(text)
                    print(f"AI responds: {response}")
                    try:
                        await speak(response)
                    except Exception as e:
                        print(f"Error in speech synthesis: {e}")
                    save_conversation()
                    print("Ready for next command...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSaving conversation and exiting...")
        save_conversation()
    except Exception as e:
        print(f"An error occurred: {e}")
        save_conversation()
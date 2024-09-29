import asyncio
from .config import transcription_queue, speech_queue, profile_info
from .profile_manager import update_profile_info, create_user_profile, get_next_profile_question
from .gpt_interface import get_gpt_response
from .audio_processing import listen_and_transcribe
import json

async def manage_conversation():
    conversation_history = []
    profile_created = False

    async def ai_speak(text):
        await speech_queue.put(json.dumps({"type": "speech", "content": text}))
        conversation_history.append({"role": "assistant", "content": text})

    while True:
        # Start listening for user input
        listen_task = asyncio.create_task(listen_and_transcribe())
        user_input = await transcription_queue.get()
        
        if user_input is None:
            if profile_created:
                await speech_queue.put(json.dumps({
                    "type": "end",
                    "profile": profile_info,
                    "flowchart": "Flowchart based on conversation"  # You'd generate this based on the conversation
                }))
                return profile_info
            else:
                await ai_speak("I'm sorry, I didn't catch that. Could you please repeat?")
                continue

        conversation_history.append({"role": "user", "content": user_input})
        
        if await update_profile_info(user_input, conversation_history):
            print("Updated profile info:", {k: v for k, v in profile_info.items() if v is not None})
            if all(profile_info.values()) and not profile_created:
                profile = await create_user_profile(conversation_history)
                await ai_speak(f"Thank you for sharing. Based on what you've told me, here's a summary of your profile: {profile}")
                profile_created = True
                await speech_queue.put(json.dumps({
                    "type": "end",
                    "profile": profile,
                    "flowchart": "Flowchart based on conversation"  # You'd generate this based on the conversation
                }))
                return profile_info
            else:
                next_question = await get_next_profile_question(conversation_history)
                if next_question:
                    await ai_speak(next_question)
                else:
                    response = await get_gpt_response(conversation_history)
                    await ai_speak(response)
        else:
            response = await get_gpt_response(conversation_history)
            await ai_speak(response)
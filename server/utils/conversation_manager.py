import time
from .config import transcription_queue, speech_queue, is_speaking, profile_info
from .profile_manager import update_profile_info, create_user_profile, get_next_profile_question
from .gpt_interface import get_gpt_response

def manage_conversation():
    greeting_sent = False
    profile_created = False
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
import json
from .config import client, profile_info
from .gpt_interface import get_gpt_response

def update_profile_info(user_input, conversation_history):
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
                "challenge": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"},
                        "meets_criteria": {"type": "boolean"}
                    },
                    "description": "A simple challenge the user has faced."
                }
            }
        }
    }

    messages = [
        {"role": "system", "content": "You are an AI assistant tasked with extracting relevant user profile information from their responses and conversation history. For each piece of information, determine if it meets the criteria to be considered complete and valid. Use the entire conversation context to make nuanced judgments about the user's profile."},
        {"role": "user", "content": f"Conversation history: {json.dumps(conversation_history)}\n\nLatest user response: {user_input}"}
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

def create_user_profile(conversation_history):
    profile_message = [
        {"role": "system", "content": "You are an AI assistant tasked with creating a comprehensive user profile based on the following information and conversation history. Create a detailed and engaging summary of the user, and keep in mind that the user is from an underrepresented community however don't explicitly state this."},
        {"role": "user", "content": f"User information:\n" + "\n".join([f"{q}: {a}" for q, a in profile_info.items()]) + f"\n\nConversation history: {json.dumps(conversation_history)}"}
    ]
    return get_gpt_response(profile_message)

def get_next_profile_question(conversation_history):
    unanswered_questions = [q for q, a in profile_info.items() if a is None]
    if unanswered_questions:
        next_question = unanswered_questions[0]
        prompt_message = [
            {"role": "system", "content": "You are an AI assistant tasked with asking a specific question in a natural, conversational way. Consider the conversation history and formulate the question to flow naturally. Avoid repeating questions that have already been answered or addressed in the conversation."},
            {"role": "user", "content": f"Conversation history: {json.dumps(conversation_history)}\nQuestion to ask about: {next_question}"}
        ]
        return get_gpt_response(prompt_message)
    return None
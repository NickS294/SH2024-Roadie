from .config import client

def get_gpt_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=4096
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in AI response: {e}")
        return "I'm sorry, I'm having trouble thinking right now. Can you please repeat that?"
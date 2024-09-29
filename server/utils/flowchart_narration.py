from .audio_processing import speak
from .gpt_interface import get_gpt_response

PROMPT = """
You are speaking directly to the person whose career plan is depicted in this Mermaid flowchart. Summarize their plan in a concise, engaging way, as if you're having a conversation with them. Use "you" and "your" to address them directly. Highlight key decisions and outcomes. Aim for a 10-second verbal delivery.

Flowchart:
{flowchart}

Provide your summary, speaking directly to the person:
"""
def narrate_flowchart(flowchart):
    prompt = PROMPT.format(flowchart=flowchart)
    messages= [{"role": "system", "content": "You are a supportive career coach speaking directly to your client. You communicate in a warm, encouraging manner, translating complex career paths into clear, actionable insights."}
               ,{"role": "user", "content": prompt}]
    try:
        narrative= get_gpt_response(messages)
        
        return narrative

    except Exception as e:
        print(f"Error: {e}")
        return "I'm sorry, I encountered an error while generating the narrative summary."
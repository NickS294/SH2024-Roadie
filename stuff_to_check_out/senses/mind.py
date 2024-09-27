import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from collections import deque
import asyncio

__all__ = ['think', 'save_conversation', 'load_conversation']

load_dotenv()

client = AsyncOpenAI(api_key=os.environ['OPENAI_API_KEY'])

MAX_MEMORY = 10 
MAX_SUMMARY_TOKENS = 500 

class ConversationMemory:
    def __init__(self):
        self.recent_memory = deque(maxlen=MAX_MEMORY)
        self.summary = ""

    def add(self, role, content):
        self.recent_memory.append({"role": role, "content": content})
        if len(self.recent_memory) == MAX_MEMORY:
            asyncio.create_task(self._update_summary())

    def get_context(self):
        context = [{"role": "system", "content": f"Conversation summary: {self.summary}"}]
        context.extend(list(self.recent_memory))
        return context

    async def _update_summary(self):
        messages = [
            {"role": "system", "content": "Summarize the following conversation, focusing on key points and context that might be relevant for future interactions. Keep the summary concise."},
            {"role": "user", "content": f"Current summary: {self.summary}\n\nNew conversation to incorporate: " + json.dumps(list(self.recent_memory))}
        ]
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=MAX_SUMMARY_TOKENS
        )
        self.summary = response.choices[0].message.content

    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump({
                'summary': self.summary,
                'recent_memory': list(self.recent_memory)
            }, f)

    def load(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            self.summary = data['summary']
            self.recent_memory = deque(data['recent_memory'], maxlen=MAX_MEMORY)

conversation_memory = ConversationMemory()

async def think(text):
    conversation_memory.add("user", text)

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
    ] + conversation_memory.get_context()

    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150
    )

    reply = response.choices[0].message.content
    conversation_memory.add("assistant", reply)

    return reply

def save_conversation(filename='conversation_history.json'):
    conversation_memory.save(filename)

def load_conversation(filename='conversation_history.json'):
    if os.path.exists(filename):
        conversation_memory.load(filename)
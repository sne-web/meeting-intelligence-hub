import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def get_client():
    """Creates and returns a Groq client."""
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. "
            "Please add it to your backend/.env file."
        )
    
    return Groq(api_key=api_key)

def ask_claude(prompt: str, system: str = None, max_tokens: int = 2000) -> str:
    """
    Sends a message to Groq and returns the response as a string.
    We kept the function name as ask_claude so we don't have to
    change any other file — they all still call ask_claude() as normal.
    
    prompt     — the user message to send
    system     — optional system prompt setting the AI's behaviour
    max_tokens — maximum length of the response
    """
    client = get_client()
    
    messages = []
    
    # Groq uses the same message format as OpenAI
    # System prompt goes as a separate message with role "system"
    if system:
        messages.append({"role": "system", "content": system})
    
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        # llama-3.3-70b is Groq's best free model
        # excellent at following JSON formatting instructions
        model="llama-3.3-70b-versatile",
        max_tokens=max_tokens,
        messages=messages
    )
    
    # Groq response format is slightly different from Anthropic
    # but we extract the text the same way
    return response.choices[0].message.content
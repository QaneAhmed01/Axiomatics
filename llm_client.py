from typing import Any, Dict, Optional
import os

try:
    import openai
except ImportError:
    openai = None #Checks if it has been installed
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(".env.local") #Loading my API key from .env.local file 



class LLMClient: 
    def __init__(self, provider:str = "openai", model: str="gpt-4o-mini"):
        self.provider = provider #Stores the provider name
        self.model = model #Stores the model name

        "client = LLMClient()"
        "client.provider='openai'"
        "client.model='gpt-4o-mini'"

        if provider == "openai":
            if openai is None:
                raise RuntimeError("openai package not installed") #Checks if openai package is installed
            key=os.getenv("OPENAI_API_KEY")
            if not key:
                raise RuntimeError ("Set OPENAI_API_KEY in environment")
        self.client = OpenAI(api_key=key)


    def generate(self, system_prompt: str, user_prompt: str, temperature: float=0.0) -> str:
        if self.provider == "openai":
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt}, #System instructions
                    {"role": "user", "content": user_prompt}, # User request
                ],
                temperature=temperature, #Sampling temp (no randomness)
                max_tokens=1500 # Max response length
               )
            return resp.choices[0].message.content #Returns the generated text from LLM
        else:
            raise NotImplementedError("provider not implemented") #Just a placeholder 


from llm_client import LLMClient
from prompt_templates import SYSTEM_BASE, DRAFT_PROMPT
import json

class DesignerAgent:
    def __init__(self, llm:LLMClient):
        self.llm = llm #Here I store LLM client for generating the API designs 

    def propose(self, user_request:str)->dict: 
        prompt=DRAFT_PROMPT.format(user_req=user_request) #Building the design prompt from the template
        raw=self.llm.generate(SYSTEM_BASE,prompt,temperature=0.0) #Generating the API using LLM

        try:
                text=raw.strip() #Removing whitspaces 
                return json.loads(text) #Trying to parse the output as JSON
        except Exception:
            start=raw.find("{") #If the previous method failed I try to locate the start of JSON
            end=raw.rfind("}") #And the end of JSON
        if start != -1 and end != -1:
            try:
                return json.loads(raw[start:end+1])  #Trying to parse the extracted JSON part
            except Exception as e:
                raise ValueError (f"Could not parse agent output as JSON. Raw output:\n{raw}") from e 
        raise ValueError(f"Could not parse agent output as JSON. Raw Output:\n{raw}") #Final fallback

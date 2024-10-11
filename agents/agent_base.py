


import sys
import os
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)
from agents.llm_base import LLM
from jinja2 import Template
import json
import os


class AgentBase(LLM):
    def __init__(self, prompt_template):
        super().__init__()
        self.prompt_template = prompt_template

    def render_prompt(self, **kwargs): 
        prompt = Template(self.prompt_template)
        x = prompt.render(**kwargs)
        return x
    
    def generate_response(self, prompt):
        output = None
        while not isinstance(output, dict):
            try:
                print("trying to parse")
                response, completion_tokens, prompt_tokens, total_tokens = self.step(prompt)
                output = json.loads(response)
                return output, prompt, completion_tokens, prompt_tokens, total_tokens
            except Exception as e:
                pass

    def generate_response_raw(self, prompt):
        response, completion_tokens, prompt_tokens, total_tokens = self.step_raw(prompt)
        return response, prompt, completion_tokens, prompt_tokens, total_tokens
       

        
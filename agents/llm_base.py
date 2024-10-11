from openai import OpenAI
import os
import re
import json


class LLM:
    def __init__(self, openai_model_name='gpt-4o-mini'):
        self.llm =OpenAI(api_key="")
        self.openai_model_name = openai_model_name


    def response_parser(self, response):
        return response.choices[0].message.content, response.usage.completion_tokens, response.usage.prompt_tokens, response.usage.total_tokens
    
    def response_parser_omni(self, response):
        import re
        response_content = response.choices[0].message.content
        start = response_content.find('{')
        end = response_content.rfind('}') + 1

        response_final = response_content[start:end]
        return response_final.strip(), response.usage.completion_tokens, response.usage.prompt_tokens, response.usage.total_tokens
    
    def response_parser_raw(self, response):
        response_content = response.choices[0].message.content
        return response_content.strip(), response.usage.completion_tokens, response.usage.prompt_tokens, response.usage.total_tokens

    
    def initialise_llm(self, api_key):
        self.llm = OpenAI(api_key=api_key)

    def step(self, prompt):
       
        response =  self.llm.chat.completions.create(
            model=self.openai_model_name,
            messages=[
                {"role": "user", "content": prompt}],
        )
        try:
            response, completion_tokens, prompt_tokens, total_tokens = self.response_parser_omni(response=response)
            return  response, completion_tokens, prompt_tokens, total_tokens 
        except:
            ValueError("Parsed failed at llm base class")


    def step_raw(self, prompt):
        response =  self.llm.chat.completions.create(
            model=self.openai_model_name,
            messages=[
                {"role": "user", "content": prompt}],
        )
        try:
            response, completion_tokens, prompt_tokens, total_tokens = self.response_parser_raw(response=response)
            return  response, completion_tokens, prompt_tokens, total_tokens 
        except:
            ValueError("Parsed failed at llm base class")



# llm = LLM()
# print(llm.step("what is your"))

 # print(pr)
        # response = llm.invoke(prompt)
        # print(response)
        # return response
        # response = client.chat.completions.create(
        #     model=" mistralai/Mixtral-8x22B-Instruct-v0.1",
        #     messages=[{"role": "user", "content": prompt}],
        # )
        # print(response.choices[0].message.content)
        # return response.choices[0].message.content  
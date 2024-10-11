import sys
import os
import asyncio
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)

from agents.agent_base import AgentBase
from prompt.prompts import *
from utils.code_formatter import format_code_history
from utils.MongoDBDecorator import MongoDBDecorator
from utils.check_args import check_args
from utils.event_emitter import event_emitter


#***************************************************************************************
#********************** RecommendationAgent ********************************************
#***************************************************************************************

class RouterAgent(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=USER_INTENT_MAPPER_PROMPT)
        self.name = "RouterAgent"

    def parse_response(self, response):
        return response['route']
    
    @check_args
    @MongoDBDecorator(db_name='internal_agent', collection_name='logs')
    async def reply(self, conversation_history, current_route, user_question, message_id ,sid):
        router_prompt = self.render_prompt(
            conversation_history=conversation_history, 
            current_route=current_route,
            user_question=user_question
        )
        response, prompt, completion_tokens, prompt_tokens, total_tokens = self.generate_response(router_prompt)


        cost = (prompt_tokens / 1000000) * 0.15 + (completion_tokens  / 1000000 ) * 0.600 
        logs = {
            'session_id': sid,
            'message_id':message_id,
            'name': self.name,
            'response': response,
            'prompt': prompt,
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens,
            'total_tokens': total_tokens,
            'conversation_history': conversation_history,
            'user_question': user_question,
            'cost': cost
        }
        
        await event_emitter.emit('log', sid, logs)

        route = self.parse_response(response)

        return route, logs


#***************************************************************************************
#********************** RecommendationAgent ********************************************
#***************************************************************************************
    
class RecommendationAgent(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=RECOMMENDATION_AGENT_PROMPT) 
        self.name = "RecommendationAgent"   

    def parse_response(self, response):
        return response['tool_name'], response['tool_args']
    
    @check_args
    @MongoDBDecorator(db_name='internal_agent', collection_name='logs')
    async def reply(self, conversation_history, user_question, sid, message_id):
        
        recommendation_agent_prompt = self.render_prompt(
                conversation_history=conversation_history, 
                user_question=user_question,
                
            )
        
        response, prompt, completion_tokens, prompt_tokens, total_tokens = self.generate_response(recommendation_agent_prompt)
        
        cost = (prompt_tokens / 1000000) * 0.15 + (completion_tokens  / 1000000 ) * 0.600 

        logs = {
            'session_id': sid,
            'message_id': message_id,
            'name': self.name,
            'response': response,
            'prompt': prompt,
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens,
            'total_tokens': total_tokens,
            'conversation_history': conversation_history,
            'user_question': user_question,
            'cost': cost

        }

        await event_emitter.emit('log', sid, logs)

        action, action_args = self.parse_response(response)
        
        return (action, action_args), logs


#***************************************************************************************
#********************** SalesmanAgent **************************************************
#***************************************************************************************
    
class SalesmanAgent(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=SALES_AGENT_PROMPT)
        self.name = "SalesmanAgent"

    def parse_response(self, response):
        return response['response']
    
    @check_args
    @MongoDBDecorator(db_name='internal_agent', collection_name='logs')
    async def reply(self, user_question, context, language, sid, message_id):
        responder_prompt = self.render_prompt(
                        user_question=user_question, 
                        context=context, 
                        language=language
                    )
        response, prompt, completion_tokens, prompt_tokens, total_tokens = self.generate_response(responder_prompt)
        
        cost = (prompt_tokens / 1000000) * 0.15 + (completion_tokens  / 1000000 ) * 0.600 

        logs = {
            'session_id': sid,
            'message_id': message_id,
            'name': self.name,
            'response': response,
            'prompt': prompt,
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens,
            'total_tokens': total_tokens,
            'user_question': user_question,
            'cost': cost
        }

        await event_emitter.emit('log', sid, logs)

        final_response = self.parse_response(response)

        return final_response, logs



#***************************************************************************************
#********************** PolicyGuidanceAgent ********************************************
#***************************************************************************************
    

class PolicyGuidanceAgent(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=POLICY_GUIDANCE_AGENT_PROMPT)
        self.name = "PolicyGuidanceAgent"

    def parse_response(self, response):
        return response['response']
    
    @check_args
    @MongoDBDecorator(db_name='internal_agent', collection_name='logs')
    async def reply(self, user_question, company_policy_content, user_language, sid, message_id):
        policy_guidance_prompt = self.render_prompt(
            user_question=user_question, 
            company_policy_content=company_policy_content, 
            user_language=user_language
        )

        response, prompt, completion_tokens, prompt_tokens, total_tokens = self.generate_response(policy_guidance_prompt)

        cost = (prompt_tokens / 1000000) * 0.15 + (completion_tokens  / 1000000 ) * 0.600 


        logs = {
            'session_id': sid,
            'message_id': message_id,
            'name': self.name,
            'response': response,
            'prompt': prompt,
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens,
            'total_tokens': total_tokens,
            'user_question': user_question,
            'cost': cost

        }

        await event_emitter.emit('log', sid, logs)

        response = self.parse_response(response)

        return response, logs



#***************************************************************************************
#********************** UnrelatedRouteAgent ********************************************
#***************************************************************************************
    

class UnrelatedRouteAgent(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=UNRELATED_ROUTE_AGENT_PROMPT)
        self.name = "UnrelatedRouteAgent"

    def parse_response(self, response):
        return response['response']
    
    @check_args
    @MongoDBDecorator(db_name='internal_agent', collection_name='logs')
    async def reply(self, user_question, user_language, sid, message_id):
        
        unrelated_route_prompt = self.render_prompt(
            user_question=user_question, 
            user_language=user_language
        )

        
        response, prompt, completion_tokens, prompt_tokens, total_tokens = self.generate_response(unrelated_route_prompt)

        cost = (prompt_tokens / 1000000) * 0.15 + (completion_tokens  / 1000000 ) * 0.600 

        logs = {
            'session_id': sid,
            'message_id': message_id,
            'name': self.name,
            'response': response,
            'prompt': prompt,
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens,
            'total_tokens': total_tokens,
            'user_question': user_question,
            'cost': cost
        }

        await event_emitter.emit('log', sid, logs)

        response = self.parse_response(response)

        return response, logs
        
    

#***************************************************************************************
#********************** PlannerAgent ***************************************************
#***************************************************************************************

class PlannerAgent(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=PLANNER_PROMPT)
        self.name = "PlannerAgent"

    def parse_response(self, response):
        print(response)
        return response['tasks']
    
    
    @check_args
    @MongoDBDecorator(db_name='internal_agent', collection_name='logs')
    async def reply(self, conversation_history, user_question, sid, message_id):
        planner_prompt = self.render_prompt(conversation_history=conversation_history, user_question=user_question)
        response, prompt, completion_tokens, prompt_tokens, total_tokens = self.generate_response(planner_prompt)
        tasks = self.parse_response(response)

        cost = (prompt_tokens / 1000000) * 0.15 + (completion_tokens  / 1000000 ) * 0.600 

        logs = {
            'session_id': sid,
            'message_id': message_id,
            'name': self.name,
            'response': response,
            'prompt': prompt,
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens,
            'total_tokens': total_tokens,
            'conversation_history': conversation_history,
            'user_question': user_question,
            'cost': cost

        }

        await event_emitter.emit('log', sid, logs)

        return tasks, logs
    

#***************************************************************************************
#********************** DataFetchRouter ************************************************
#***************************************************************************************
    
class BaseRouter(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=BASE_ROUTER_PROMPT)
        self.name = "BaseRouter"

    def parse_response(self, response):
        return response['route']
    
    @check_args
    @MongoDBDecorator(db_name='internal_agent', collection_name='logs')
    async def reply(self, current_task, sid, message_id):
        base_router_prompt = self.render_prompt(current_task=current_task)
        response, prompt, completion_tokens, prompt_tokens, total_tokens = self.generate_response(base_router_prompt)
        route = self.parse_response(response)

        cost = (prompt_tokens / 1000000) * 0.15 + (completion_tokens  / 1000000 ) * 0.600 


        logs = {
            'session_id': sid,
            'message_id': message_id,
            'name': self.name,
            'current_task': current_task,
            'prompt': prompt,
            'response': response,
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens,
            'total_tokens': total_tokens,
            'cost': cost
  
        }

        await event_emitter.emit('log', sid, logs)

        return route, logs
    


#***************************************************************************************
#********************** DataFetchRouter ************************************************
#***************************************************************************************
    
class DataFetchRouter(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=DATA_FETCH_ROUTER)
        self.name = "DataFetchRouter"

    def parse_response(self, response):
        return response['route']
    


#***************************************************************************************
#********************** DataAgent ******************************************************
#***************************************************************************************

class DataAgent(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=BASE_DATA_FETCHER_AGENT)
        self.name = "DataAgent"

    def parse_response(self, response):
        return response['thought'], response['python_code']
    
    @check_args
    @MongoDBDecorator(db_name='internal_agent', collection_name='logs')
    async def reply(self, current_task, DATASET_PROMPT, conversation_history, code_history, feedback, sid, message_id):
        data_agent_prompt = self.render_prompt(current_task=current_task,
                                               data=DATASET_PROMPT,
                                               conversation_history=conversation_history,
                                               code_history=code_history,
                                               feedback=feedback)
        

        response, prompt, completion_tokens, prompt_tokens, total_tokens = self.generate_response(data_agent_prompt)
       
        cost = (prompt_tokens / 1000000) * 0.15 + (completion_tokens  / 1000000 ) * 0.600 

        logs = {
            'session_id': sid,
            'message_id': message_id,
            'name': self.name,
            'current_task': current_task,
            'prompt': prompt,
            'response': response,
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens,
            'total_tokens': total_tokens,
            'cost': cost
        }

        await event_emitter.emit('log', sid, logs)

        thought, code = self.parse_response(response)
        return (thought, code), logs
    



#***************************************************************************************
#********************** DataAgentCodeAct ***********************************************
#***************************************************************************************

class DataAgentCodeAct(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=BASE_DATA_FETCHER_AGENT_CA)
        self.name = "DataAgent"
    
    def execute_code_from_string(self,response):
        import re
        code_block = re.search(r"<execute>(.*?)</execute>", response, re.DOTALL)
    
        if code_block:
            code = code_block.group(1).strip()  # Extract the code and strip any leading/trailing whitespace
            return code
        else:
            return "No <execute> block found."
    
    @check_args
    @MongoDBDecorator(db_name='internal_agent', collection_name='logs')
    async def reply(self, current_task, DATASET_PROMPT='', conversation_history=[], code_history='', feedback='', sid='', message_id=''):
        data_agent_prompt = self.render_prompt(current_task=current_task,
                                               data=DATASET_PROMPT,
                                               conversation_history=conversation_history,
                                               code_history=code_history,
                                               feedback=feedback)
        

        response, prompt, completion_tokens, prompt_tokens, total_tokens = self.generate_response_raw(data_agent_prompt)
       
        cost = (prompt_tokens / 1000000) * 0.15 + (completion_tokens  / 1000000 ) * 0.600 
        res = self.execute_code_from_string(response)

        logs = {
            'session_id': sid,
            'message_id': message_id,
            'name': self.name,
            'current_task': current_task,
            'prompt': prompt,
            'response': res,
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens,
            'total_tokens': total_tokens,
            'cost': cost
        }
        
        # print(response)

        await event_emitter.emit('log', sid, logs)


        # print("Parsed Code: ")
        # res = self.execute_code_from_string(response)
        # print(res)
        # await event_emitter.emit('log', sid, logs)

        # thought, code = self.parse_response(response)
        thought = ""
        return (thought, res), logs
    

# data_agent = DataAgentCodeAct()
# data_agent.reply("calculate the square root of 988231")

#***************************************************************************************
#********************** XgboostAgent ***************************************************
#***************************************************************************************
    
class XgboostAgent(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=XGBOOST_AGENT_PROMPT)

    def parse_response(self, response):
        return response['thought'], response['python_code']
    


#***************************************************************************************
#********************** Task Modifier Agent ********************************************
#***************************************************************************************
 
class TaskModifierAgent(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=TASK_MODIFIER_PROMPT)
        self.name = "TaskModifierAgent"

    def parse_response(self, response):
        return response['modify'], response['task_number'], response['feedback']
    
    @check_args
    @MongoDBDecorator(db_name='internal_agent', collection_name='logs')
    async def reply(self, code_history, current_task_with_id, sid, message_id):
        task_modifier_prompt = self.render_prompt(code_history=code_history, current_task_with_id=current_task_with_id)
        print(task_modifier_prompt)
        response, prompt, completion_tokens, prompt_tokens, total_tokens = self.generate_response(task_modifier_prompt)
        
        cost = (prompt_tokens / 1000000) * 0.15 + (completion_tokens  / 1000000 ) * 0.600 

        
        logs = {
            'session_id': sid,
            'message_id': message_id,
            'name': self.name,
            'code_history': code_history,
            'current_task': current_task_with_id,
            'prompt': prompt,
            'response': response,
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens,
            'total_tokens': total_tokens,
            'cost': cost

        }

        await event_emitter.emit('log', sid, logs)

        modify, task_number, feedback = self.parse_response(response)
        return (modify, task_number, feedback), logs


class DataTaskPlannerAgent(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=BASE_DATA_PLANNER)

    def parse_response(self, response):
        return response['tasks']
    




#***************************************************************************************
#********************** Responder Agent ************************************************
#***************************************************************************************
class ResponderAgent(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=RESPONDER_PROMPT)
        self.name = "ResponderAgent"

    def parse_response(self, response):
        return response['response'], response['file_name']
    
    @check_args
    @MongoDBDecorator(db_name='internal_agent', collection_name='logs')
    async def reply(self, context, user_question, conversation_history, sid, message_id):
        responder_agent = self.render_prompt(context=context, user_question=user_question ,conversation_history=conversation_history)
        response, prompt, completion_tokens, prompt_tokens, total_tokens = self.generate_response(responder_agent)
        
        cost = (prompt_tokens / 1000000) * 0.15 + (completion_tokens  / 1000000 ) * 0.600 

        logs = {
            'session_id': sid,
            'message_id': message_id,
            'name': self.name,
            'context': context,
            'conversation_history': conversation_history,
            'prompt': prompt,
            'response': response,
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens,
            'total_tokens': total_tokens,
            'cost': cost

        }

        await event_emitter.emit('log', sid, logs)

        response, file_name = self.parse_response(response)


        return (response, file_name), logs
    


#***************************************************************************************
#**********************Master Router Agent *********************************************
#***************************************************************************************
class MasterRouterAgent(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=MASTER_ROUTER_AGENT_PROMPT)
        self.name = "MasterRouterAgent"

    def parse_response(self, response):
        return response['route']
    
    @check_args
    @MongoDBDecorator(db_name='internal_agent', collection_name='logs')
    async def reply(self, user_question, conversation_history, sid, message_id):
        master_router_agent_prompt = self.render_prompt(user_question=user_question, conversation_history=conversation_history)
        print(f"Master Router Agent Prompt > {master_router_agent_prompt}")
        response, prompt, completion_tokens, prompt_tokens, total_tokens = self.generate_response(master_router_agent_prompt)

        cost = (prompt_tokens / 1000000) * 0.15 + (completion_tokens  / 1000000 ) * 0.600 

        logs = {
            'session_id': sid,
            'message_id': message_id,
            'name': self.name,
            'conversation_history': conversation_history,
            'prompt': prompt,
            'response': response,
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens,
            'total_tokens': total_tokens,
            'cost': cost

        }

        await event_emitter.emit('log', sid, logs)

        route = self.parse_response(response)

        return route, logs


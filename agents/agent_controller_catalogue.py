import sys
import os
import asyncio

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)

from prompt.prompts import *
from utils.logger import Logger
from agents.agent_base import AgentBase
from jinja2 import Template
from categories.CategoryBase import Categories
from API.get_company_policy_api import get_company_policy_api
from API.recommendation_api import recommendation_api
import time

from agents.agenthub import *

logger = Logger()

# class RouterAgent(AgentBase):
#     def __init__(self):
#         super().__init__(prompt_template=USER_INTENT_MAPPER_PROMPT)

#     def parse_response(self, response):
#         return response['route']
    
class CategoryMapperAgent(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=CATEGORY_MAPPER_PROMPT)

    def parse_response(self, response):
        return response['categories']
    
class QueryAugmentorAgent(AgentBase):
    def __init__(self):
        super().__init__(prompt_template=SEARCH_QUERY_AUGMENTOR_PROMPT)    

    def parse_response(self, response):
        return response['augmented_search_query']
    
# class RecommendationAgent(AgentBase):
#     def __init__(self):
#         super().__init__(prompt_template=RECOMMENDATION_AGENT_PROMPT)    

#     def parse_response(self, response):
#         return response['tool_name'], response['tool_args']
    
# class SalesmanAgent(AgentBase):
#     def __init__(self):
#         super().__init__(prompt_template=SALES_AGENT_PROMPT)

#     def parse_response(self, response):
#         return response['response']

# class PolicyGuidanceAgent(AgentBase):
#     def __init__(self):
#         super().__init__(prompt_template=POLICY_GUIDANCE_AGENT_PROMPT)

#     def parse_response(self, response):
#         return response['response']
    
# class UnrelatedRouteAgent(AgentBase):
#     def __init__(self):
#         super().__init__(prompt_template=UNRELATED_ROUTE_AGENT_PROMPT)

#     def parse_response(self, response):
#         return response['response']
    
class AgentController:
    def __init__(self, socket_send_message, send_products, send_agent_status, send_logs,  user_language: str = "English", ):
        super().__init__()
        self.router_agent = RouterAgent()
        self.category_mapper_agent = CategoryMapperAgent()
        self.query_augmentor_agent = QueryAugmentorAgent()
        self.recommendation_agent = RecommendationAgent()
        self.salesman_agent = SalesmanAgent()
        self.policy_guidance_agent = PolicyGuidanceAgent()
        self.unrelated_route_agent = UnrelatedRouteAgent()

        self.route = None
        self.conversation_history = []
        self.recommendation_follow_up_questions = False
        self.interested_categories = None
        self.categories_features = None
        self.category = Categories()
        self.augmented_search_query = None
        self.user_language = user_language
        self.followup_question = False
        self.end = False

        self.socket_send_message = socket_send_message
        self.send_products = send_products
        self.send_logs = send_logs

        self.send_agent_status = send_agent_status

        # Event to wait for user input
        self.user_input_event = asyncio.Event()
        self.waiting_for_details = False
        self.sid = None

    async def recommendation_route(self, user_question):
        while True:
            action, action_args = self.recommendation_agent.reply(
                conversation_history=self.format_conversation(), 
                user_question=user_question,
                sid=self.sid

            )

            # 
            # await self.send_logs(sid=self.sid, logs=f"Recommendation agent prompt\n {recommendation_agent_prompt}")

            logger.log(f"Action: {action}\nAction Args: {action_args}", role="Recommendation Agent", color='neon_purple')
            # await self.send_logs(sid=self.sid, logs=f"Action: {action}\nAction Args: {action_args}")

            if action == 'recommendation_api':

                await self.send_agent_status(self.sid, "Searching Catalog...")
                # await self.send_logs(sid=self.sid, logs="Searching Catalog...")

                product_information, explanation = await recommendation_api(**action_args)
                logger.log(product_information, color='neon_green', role="Response from Recommendation API")
                # await self.send_logs(sid=self.sid, logs=f"Response from Recommendation API: {product_information}")

                if product_information: 
                    final_response = self.salesman_agent.reply(
                        user_question=user_question, 
                        context=explanation, 
                        language=self.user_language,
                        sid=self.sid
                    )
                    print(final_response)
                    # await self.send_logs(sid=self.sid, logs=f"Final response: {final_response}")
                    response = {"product_list": product_information, "data": final_response}

                    
                    await self.socket_send_message(self.sid, response)
                    
                    return final_response

            if action == 'engage_with_user':
                # await self.send_logs(sid=self.sid, logs=f"Engage with user: {action_args['question_or_recommendation']}")
                await self.socket_send_message(self.sid, {"data": action_args['question_or_recommendation']})

                # Set the flag to wait for user input
                self.waiting_for_details = True
                await self.user_input_event.wait()
                self.user_input_event.clear()  # Reset the event for the next wait

                # Continue the loop with the new user input
                self.waiting_for_details = False


    def format_conversation(self):
        conversation = ""
        for conv in self.conversation_history:
            if conv['role'] == "AI":
                conversation += f"Your Reply: {conv['content']}\n"
            else:
                conversation += f"User: {conv['content']}\n"
        return conversation
    

    async def company_policy_route(self, user_question):

        # await self.send_logs(sid=self.sid, logs=f"Company policy route")
        policy_content = await get_company_policy_api(query_string=user_question)

        response = await self.policy_guidance_agent.reply(
            user_question=user_question, 
            company_policy_content=policy_content, 
            user_language=self.user_language,
            sid=self.sid,
            message_id=self.message_id

        )

        # await self.send_logs(sid=self.sid, logs=f"Policy Guidance Agent: {response}")

        await self.socket_send_message(self.sid, {"data": response, 'message_id': self.message_id})

        return response
    
    async def unrelated_route(self, user_question):
        # await self.send_logs(sid=self.sid, logs=f"Unrelated route")
        
        response = await self.unrelated_route_agent.reply(
            user_question=user_question, 
            user_language=self.user_language,
            sid=self.sid,
            message_id=self.message_id

        )

        # await self.send_logs(sid=self.sid, logs=f"Unrelated route response: {response}")
        await self.socket_send_message(self.sid, {"data": response, 'message_id': self.message_id})
        return response

    async def initiate_chat(self, user_question):
        logger.log("Initiating chat with user question: " + str(user_question), color='white', role='Customer')

        self.route = await self.router_agent.reply(
            conversation_history=self.conversation_history, 
            current_route=self.route,
            user_question=user_question,
            sid=self.sid,
            message_id=self.message_id
        )

        logger.log("Routing to: " + self.route, color='neon_green', role='Router')
        # await self.send_logs(sid=self.sid, logs=f"Routing to: {self.route}")

        if self.route == "recommendation_route":
            await self.recommendation_route(user_question=user_question)

        elif self.route == 'company_policy_route':
            await self.company_policy_route(user_question=user_question)

        elif self.route == 'unrelated_route':
            await self.unrelated_route(user_question=user_question)
    
    async def handle_user_message(self, user_response, message_id, sid, conversation_history):
        self.sid = sid
        self.message_id = message_id
        self.conversation_history = conversation_history

        logger.log("Handling user message: " + user_response, color='white', role='Handler')
        # await self.send_logs(sid=self.sid, logs=f"Handling user message: {user_response}")

        
        if self.waiting_for_details:
            logger.log("Waiting for details, setting user input event", color='yellow', role='Handler')
            self.user_input_event.set()  # Set the event to continue processing
        
        else:
            logger.log("User input event already set, initiating chat", color='yellow', role='Handler')
            await self.initiate_chat(user_response)



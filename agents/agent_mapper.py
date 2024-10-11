import sys
import os
import asyncio
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)

from agents.agent_controller_catalogue import AgentController as AgentControllerCatalog
from agents.agent_controller_ds import AgentController as AgentControllerDS
from agents.agent_base import AgentBase
from prompt.prompts import *
import asyncio

from agents.agenthub import MasterRouterAgent


class MasterAgentController:
    def __init__(self, socket_send_message, send_products, send_agent_status, send_logs):
        self.agent_controller_catalogue = AgentControllerCatalog(socket_send_message=socket_send_message, send_products=send_products, send_agent_status=send_agent_status, send_logs=send_logs)
        self.agent_controller_ds = AgentControllerDS(socket_send_message=socket_send_message, send_logs=send_logs)
        self.master_router_agent = MasterRouterAgent()
        self.socket_send_message = socket_send_message
        self.send_logs = send_logs

        self.conversation_history = []

    def format_questions(self):
        user_questions = ""
        for i, question in enumerate(self.conversation_history,):
            user_questions += f'Question {i+1}: {question}\n'
        return user_questions

    async def initiate_chat(self, user_message, message_id, DATASET_PROMPT, sid, conversation_history):
        route = await self.master_router_agent.reply(user_question=user_message, 
                                               conversation_history=conversation_history,
                                               sid=sid,
                                               message_id=message_id)
        print("Route decided: ", route)
        # await self.send_logs(sid=sid, logs=f"Route decided: {route}")
        if route.strip() == 'catalog_data_route':
            print("Entering catalog_data_route")
            # await self.send_logs(sid=sid, logs="Entering catalog_data_route")
            ## Old Data Science
            ## why it is important to know the customer here? to make right api call?
            await self.agent_controller_ds.handle_user_message(user_message, message_id, DATASET_PROMPT, sid, conversation_history)
        
        if route.strip() == 'internal_company_route':
            print("Entering internal_company_route")
            # await self.send_logs(sid=sid, logs="Entering internal_company_route")
            ## Catalog agent
            await self.agent_controller_catalogue.handle_user_message(user_message, message_id, sid, conversation_history)

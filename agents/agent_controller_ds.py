import sys
import os
import asyncio
from typing import Dict, List

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_dir)

from utils.task import Task
from utils.logger import Logger
from utils.code_formatter import format_code_history
from utils.feedback_agent_datastore import FeedbackAgentLogs
from utils.jupyter_client_1 import JupyterClient
from bs4 import BeautifulSoup
import json
from utils.event_emitter import event_emitter
from utils.code_history_manager import code_history_manager
from agents.agenthub import *

logger = Logger()



class AgentController:
    def __init__(self, socket_send_message, send_logs):
        self.planner_agent = PlannerAgent()
        self.base_router_agent = BaseRouter()
        self.data_agent = DataAgentCodeAct()
        self.xgboost_agent = XgboostAgent()
        self.task_modifier_agent = TaskModifierAgent()
        self.data_planner_agent = DataTaskPlannerAgent()
        self.responder_agent = ResponderAgent()

        self.conversation_history = []

        self.tasks = None
        self.code_history_manager = code_history_manager
        self.data_tasks = None
        self.finish = False
        self.feedback = None
        self.sid = None
        self.message_id = None
        self.jc = JupyterClient()

        self.DATASET_PROMPT = None
        self.user_question = None

        ## Socket Connection
        self.socket_send_message = socket_send_message
        self.send_logs = send_logs

    async def task_modifier(self):
        modify, task_number, feedback = await self.task_modifier_agent.reply(
            code_history=format_code_history(self.code_history_manager.get_code_history(self.sid)),
            current_task_with_id=self.tasks.get_current_task_with_id(),
            sid=self.sid,
            message_id=self.message_id
        )
        return modify, task_number, feedback

    async def planner(self, user_question):
        logger.log(user_question, color='yellow', role="User Question")

        ## basic agent call
        tasks = await self.planner_agent.reply(
            conversation_history=self.conversation_history,
            user_question=user_question,
            sid=self.sid,
            message_id=self.message_id
        )
        self.tasks = Task(tasks)
        logger.log(self.tasks.get_task_template_with_number(), color='yellow', role="Task")

    def load_file_content(self, file_name):
        chart_data = []
        if file_name and file_name.endswith('.json'):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(root_dir, file_name)
            try:
                with open(file_path, 'r') as json_file:
                    chart_data = json.load(json_file)
            except FileNotFoundError:
                print(f"File {file_name} not found in {root_dir}.")
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file {file_name}.")
        return chart_data

    async def responder_agent_handler(self):
        response, file_name = await self.responder_agent.reply(
            context=format_code_history(self.code_history_manager.get_code_history(self.sid)),
            user_question=self.user_question,
            conversation_history=self.conversation_history,
            sid=self.sid,
            message_id=self.message_id
        )
        
        chart_data = self.load_file_content(file_name=file_name)
        await self.socket_send_message(self.sid, {"data": response, "file_name": file_name, "chart_data": chart_data, 'is_html': True, 'message_id': self.message_id})
        self.tasks = None
        return response

    async def forecasting_route_handler(self):
        while True:
            forecasting_prompt = self.xgboost_agent.render_prompt(
                code_history=format_code_history(self.code_history_manager.get_code_history(self.sid)),
                current_task=self.tasks.get_current_task(),
                feedback=self.feedback
            )
            logger.log(f"{forecasting_prompt}", color='neon_yellow', role='Forecasting Agent')
            response_json = self.xgboost_agent.generate_response(forecasting_prompt)
            thought, code = self.xgboost_agent.parse_response(response_json)

            session_id = self.jc.create_new_session(self.sid)
            status, response = self.jc.execute_code(code, session_id)

            logger.log(f"{code}", color='blue', role='Xgboost Agent Code')

            if status == 'Success':
                code_history = self.code_history_manager.get_code_history(self.sid)
                if code_history and not code_history[-1]['success']:
                    self.code_history_manager.update_last_code_history(self.sid, code, f"\n\n{response}", True)
                else:
                    self.code_history_manager.add_to_code_history(self.sid, code, f"\n\n{response}", True)

                self.feedback = None
                modify, task_number, feedback = await self.task_modifier()
                self.feedback = feedback

                logger.log(f"{task_number}: {modify}\n\nfeedback: {feedback}", color='neon_orange', role='Moderator Agent')
                if modify == 'successful':
                    self.tasks.update_task(task_number, 'successful')
                    break
            else:
                logger.log(f"{response}", color='red', role='Code Execution')
                self.code_history_manager.add_to_code_history(self.sid, code, f"{response}", False)

    async def data_agent_handler(self):
        for i in range(5):
            thought, code = await self.data_agent.reply(
                current_task=self.tasks.get_current_task(),
                DATASET_PROMPT=self.DATASET_PROMPT,
                conversation_history=self.conversation_history,
                code_history=format_code_history(self.code_history_manager.get_code_history(self.sid)),
                feedback=self.feedback,
                sid=self.sid,
                message_id=self.message_id
            )
            
            session_id = self.jc.create_new_session(self.sid)
            status, response = self.jc.execute_code(code, session_id)

            logger.log(f"{code}", color='neon_pink', role='Data Agent Code')

            if status == 'Success':
                self.code_history_manager.add_to_code_history(self.sid, code, f"{response}\n", True)

                logs = {
                    'session_id': self.sid,
                    'message_id': self.message_id,
                    'name': "Code Execution Successful",
                    'context': self.code_history_manager.get_code_history(self.sid),
                    'conversation_history': self.conversation_history,
                    'prompt': "",
                    'response': response,
                    'completion_tokens': 0,
                    'prompt_tokens': 0,
                    'total_tokens': 0,
                }

                await event_emitter.emit('log', self.sid, logs)


                ### TO SAVE TOKENS

                # self.feedback = None
                # modify, task_number, feedback = await self.task_modifier()
                # self.feedback = feedback

                modify = 'successful'
                task_number = self.tasks.get_current_task_id()
                feedback = ""

                logger.log(f"{task_number}: {modify}\n\nfeedback: {feedback}", color='neon_orange', role='Moderator Agent')

                if modify == 'successful':
                    self.tasks.update_task(task_number, 'successful')
                    break
            else:
                logger.log(f"{response}", color='red', role='Code Execution')
                
                logs = {
                    'session_id': self.sid,
                    'message_id': self.message_id,
                    'name': "Code Execution Failed",
                    'context': self.code_history_manager.get_code_history(self.sid),
                    'conversation_history': self.conversation_history,
                    'prompt': "",
                    'response': response,
                    'completion_tokens': 0,
                    'prompt_tokens': 0,
                    'total_tokens': 0,
                }

                self.feedback = response

                await event_emitter.emit('log', self.sid, logs)

                self.code_history_manager.add_to_code_history(self.sid, code, f"{response}", False)

                # if i == 4:
                #     await self.socket_send_message(self.sid, {"data": response})

    async def route_handler(self, route):
        if route == 'data_fetch_route':
            await self.data_agent_handler()
        elif route == 'forecasting_route':
            await self.forecasting_route_handler()
        else:
            print('unknown route')

    async def base_router(self):
        await self.send_logs(sid=self.sid, logs=f"Entering base router")
        base_router_prompt = self.base_router_agent.render_prompt(current_task=self.tasks.get_current_task())
        response = self.base_router_agent.generate_response(base_router_prompt)
        route = self.base_router_agent.parse_response(response)
        return route

    async def initiate_chat(self, user_question, max_iter=10):
        self.user_question = user_question
        logger.log(user_question, color='blue', role="User")
        for i in range(max_iter):
            if self.tasks and self.tasks.check_termination():
                response = await self.responder_agent_handler()
                logger.log(response, color='cyan', role="FINAL RESPONSE")
                print("FINISHED")
                break
            if i == 0:
                await self.planner(user_question)
            await self.route_handler('data_fetch_route')

    async def handle_user_message(self, user_response, message_id, DATASET_PROMPT, sid, conversation_history):
        self.DATASET_PROMPT = DATASET_PROMPT
        self.sid = sid
        self.message_id = message_id
        self.user_question = user_response
        self.conversation_history = conversation_history
        await self.initiate_chat(user_response)

    

# query_distinct_product_ids = '''\nSELECT DISTINCT \"item_productId\"\nFROM sales_history\n'''
# distinct_product_ids_df = fetch_postgres_data(query_distinct_product_ids)
# if not distinct_product_ids_df.empty:
#     # Proceed to calculate top selling products
#     query_top_selling_products = '''\n'''
#     top_selling_products_df = fetch_postgres_data(query_top_selling_products)
#     if len(top_selling_products_df) <= 10:
#         print(top_selling_products_df)
#     else:
#         print(top_selling_products_df.head())
#         top_selling_products_df.to_csv('top_selling_products_final_report.csv', index=False)
# else:
#     print('No matching product IDs found in sales history.')
import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import socketio
import asyncio
from agents.agent_mapper import MasterAgentController
import json
from prompt import prompts
from pydantic import BaseModel
from typing import Union
from API.catalogue_data import CatalogClient
from dotenv import load_dotenv
import re
from utils.mongo_utils import mongodb_manager
from utils.app_utils import get_update_dataset_prompt
import uuid
from utils.event_emitter import event_emitter
from utils.code_history_manager import code_history_manager
from utils.MongoDBDecorator import sum_costs_by_message_id

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Loading environment variable
load_dotenv()

# Global variables + environment variables
catalog_url = os.getenv('CATALOG_URL')
user_sessions = {}
conversation_history = {}
tasks = {}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
app_sio = socketio.ASGIApp(sio, app)

class UpdateVar(BaseModel):
    name: str
    value: Union[str, int, float, list, dict]

PROMPTS_FILE_PATH = "prompt/prompts.py"

expose_vars = {
    "test", "USER_INTENT_MAPPER_PROMPT", "CATEGORY_MAPPER_PROMPT",
    "RECOMMENDATION_AGENT_PROMPT", "SALES_AGENT_PROMPT",
    "POLICY_GUIDANCE_AGENT_PROMPT", "UNRELATED_ROUTE_AGENT_PROMPT",
    "BASE_ROUTER_PROMPT", "DATA_FETCH_ROUTER", "BASE_DATA_PLANNER",
    "BASE_DATA_FETCHER_AGENT", "TASK_MODIFIER_PROMPT", "DATASET_PROMPT",
    "RESPONDER_PROMPT", "MASTER_ROUTER_AGENT_PROMPT", "PLANNER_PROMPT"
}

def read_prompts_file():
    with open(PROMPTS_FILE_PATH, "r") as file:
        return file.read()

def write_prompts_file(content):
    backup_path = f"{PROMPTS_FILE_PATH}.bak"
    os.rename(PROMPTS_FILE_PATH, backup_path)
    try:
        with open(PROMPTS_FILE_PATH, "w") as file:
            file.write(content)
    except Exception as e:
        os.rename(backup_path, PROMPTS_FILE_PATH)
        raise e
    os.remove(backup_path)

def update_variable(content, variable_name, new_value):
    pattern = rf'{variable_name}\s*=\s*("""|\'\'\')(?P<value>.*?)(\1)'
    if re.search(pattern, content, re.DOTALL) is None:
        raise ValueError(f"Variable {variable_name} not found in the file")
    
    if isinstance(new_value, str):
        new_value_str = f'"""{new_value}"""'
    else:
        new_value_str = repr(new_value)
    
    updated_content = re.sub(
        pattern,
        f'{variable_name} = {new_value_str}',
        content,
        flags=re.DOTALL
    )
    return updated_content

@app.get("/prompts")
def get_prompts():
    attributes = []
    for k in expose_vars:
        if hasattr(prompts, k):
            try:
                value = getattr(prompts, k)
                attributes.append({"key": k, "value": value})
            except (TypeError, AttributeError):
                continue
    return attributes

@app.put("/prompts")
def update_prompt(update_var: UpdateVar):
    if update_var.name not in expose_vars:
        raise HTTPException(status_code=400, detail="Variable not allowed to be updated")
    
    try:
        file_content = read_prompts_file()
        updated_content = update_variable(file_content, update_var.name, update_var.value)
        # write_prompts_file(updated_content)
        setattr(prompts, update_var.name, update_var.value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update variable: {str(e)}")
    
    return get_prompts()

@app.get("/files/{filename}")
async def get_files(filename: str):
    if filename.lower().endswith('.csv'):
        base_dir = os.path.join("utils", "Users", "agentfiles")
        file_path = os.path.join(base_dir, filename)
    else:
        file_path = filename
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="File not found")
    

@app.get("/conversation_history/{session_id}")
async def get_conversation_history(session_id: str):
    try:
        conversation_history = mongodb_manager.get_conversation_history(session_id=session_id)
        return {"history": conversation_history}
    except Exception as e:
        logger.error(f"Error fetching conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch conversation history")

@sio.event
async def connect(sid, environ):
    logger.info(f"Connected: {sid}")
    await sio.emit('message', {'data': 'Welcome! Please provide your email and sessionId to continue.'}, to=sid)

@sio.event
async def register(sid, data):
    data = json.loads(data)
    logger.info(f"Socket Connection - Register Event - {data}")
    email = data['email']
    session_id = data['sessionId']
    room_name = f"room_{session_id}"
    user_sessions[session_id] = {'sid': sid, 'room': room_name}
    await sio.enter_room(sid, room_name)
    
    await sio.emit('register_message', {'data': f'Registered with email: {email}'}, to=sid)
    await sio.emit('message', {'data': f'Registered with email: {email}'}, to=sid)
    logger.info(f"User {email} registered with session ID: {session_id} and previous conversations loaded.")

async def send_message(session_id, message):
    print("send_message > ", message)
    print('is_html > ', message.get('is_html', False))
    session_info = user_sessions.get(session_id)
    if session_info:
        sid = session_info['sid']
        logger.info(f"Sending Message to {session_id} with sid {sid}")
        print("Message ID > ", message.get('message_id', ""))
        cost = await sum_costs_by_message_id(message_id=message.get('message_id', ""))
        print("COSTTT> ", cost)
        message['cost'] = cost
        mongodb_manager.add_to_message(session_id=session_id, 
                                       message_id=message.get('message_id', ""),
                                       sender='AI', 
                                       name="Fashion Assistant", 
                                       content=message.get('data', ""), 
                                       is_html=message.get('is_html', False), 
                                       email=message.get("email", ""), 
                                       product_list=message.get("product_list", []), 
                                       filename=message.get('filename', ''),
                                       chart_data=message.get('chart_data', []),
                                       cost=cost)
        
        await sio.emit('receive_message', message, to=sid)
    else:
        logger.info(f"Session ID {session_id} not found in user sessions.")

async def send_agent_status(session_id, status):
    session_info = user_sessions.get(session_id)
    if session_info:
        sid = session_info['sid']
        logger.info(f"Sending agent status to {session_id} with sid {sid}")
        await sio.emit('agent_status', status, to=sid)
    else:
        logger.info(f"Session ID {session_id} not found in user sessions.")

async def send_logs(session_id, logs):
    print(f"Logs > {logs}")
    session_info = user_sessions.get(session_id)
    if session_info:
        sid = session_info['sid']
        logger.info(f"Sending logs to {session_id} with sid {sid}")
        await sio.emit('logs', logs, to=sid)
    else:
        logger.info(f"Session ID {session_id} not found in user sessions.")

async def send_products(session_id, product):
    session_info = user_sessions.get(session_id)
    if session_info:
        sid = session_info['sid']
        await sio.emit('product_list', {'data': product}, to=sid)
    else:
        logger.info(f"Session ID {session_id} not found in user sessions.")

event_emitter.on('log', send_logs)

agent = MasterAgentController(socket_send_message=send_message, send_products=send_products, send_agent_status=send_agent_status, send_logs=send_logs)

@sio.event
async def chat_message(sid, data):
    user_message = json.loads(data)
    print("user message received from frontend > ", user_message)
    message = user_message['text']
    session_id = user_message['sessionId']

    code_history_manager.add_token(session_id, user_message['catalogToken'])

    prompt_data = json.loads(user_message['promptData'])
    DATASET_PROMPT = get_update_dataset_prompt(prompt_data=prompt_data)
    print("Dataset prompt > ", DATASET_PROMPT)

    unique_id = uuid.uuid4()
    message_id = str(unique_id)

    mongodb_manager.add_to_message(message_id=message_id,
                                   session_id=session_id, 
                                   sender='user', 
                                   name="User", 
                                   content=message, 
                                   email=user_message.get("email", ""))
    
    conversation_history = mongodb_manager.get_conversation_history(session_id=session_id)

    print("Conversation History > ", conversation_history)

    await send_agent_status(session_id=session_id, status="Thinking...")
    logger.info(f"Message from {message}")

    if session_id in tasks and tasks[session_id] and not tasks[session_id].done():
        tasks[session_id].cancel()
        try:
            await tasks[session_id]
        except asyncio.CancelledError:
            logger.info(f"Previous task for {session_id} was cancelled.")

    task = asyncio.create_task(agent.initiate_chat(message, message_id, DATASET_PROMPT, session_id, conversation_history))
    tasks[session_id] = task
    await task

@sio.event
async def stop_message(sid, data):
    print("HERE IN STOP MESSAGE")
    session_id = data.get('sessionId')
    print("HERE IN STOP MESSAGE SEESION ID: ", session_id)
    if session_id in tasks and tasks[session_id] and not tasks[session_id].done():
        tasks[session_id].cancel()
        try:
            await tasks[session_id]
        except asyncio.CancelledError:
            logger.info(f"Task for {session_id} was cancelled upon stop request.")
        await send_agent_status(session_id=session_id, status="Stopped")

@sio.event
async def disconnect(sid):
    session_id = next((s_id for s_id, info in user_sessions.items() if info['sid'] == sid), None)
    if session_id:
        code_history_manager.end_session(session_id)
        logger.info(f"Disconnected session: {session_id} with sid: {sid}")
        if session_id in tasks and tasks[session_id]:
            tasks[session_id].cancel()
            try:
                await tasks[session_id]
            except asyncio.CancelledError:
                logger.info(f"Task for {session_id} was cancelled upon disconnect.")
        del user_sessions[session_id]
    else:
        logger.info(f"No session found for sid: {sid}")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app_sio, host='localhost', port=5000)
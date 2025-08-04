from fastapi import APIRouter

import sys
import uuid
import traceback
from datetime import datetime
from http import HTTPStatus

from pathlib import Path
import json

from fastapi import FastAPI, Request, Response, Body
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    BotFrameworkAdapter,
)
from botbuilder.schema import Activity, ActivityTypes

from models import (
    ApiChatRequest, 
    ElasticSuiteResult, 
    ElasticSuiteAnswer
)

router = APIRouter(prefix="/api", tags=["augmented-chat"])

SETTINGS = BotFrameworkAdapterSettings("", "")
ADAPTER = BotFrameworkAdapter(SETTINGS)

async def on_error(context: TurnContext, error: Exception):
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )
    # Send a trace activity if we're talking to the Bot Framework Emulator
    if context.activity.channel_id == "emulator":
        # Create a trace activity that contains the error object
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        # Send a trace activity, which will be displayed in Bot Framework Emulator
        await context.send_activity(trace_activity)

ADAPTER.on_turn_error = on_error

@router.post("/chat")
async def chat(chat_request: ApiChatRequest = Body(...)):
    
    input_message = chat_request.message
    session_id=chat_request.session_id
    user_id=chat_request.user_id

    current_session_id = session_id if session_id else str(uuid.uuid4())

    if "liste" in input_message.lower():
        return __search_result(user_id, current_session_id)
    else: 
        return __simple_answer(user_id, current_session_id)
    

def __simple_answer(user_id, session_id):
    return ElasticSuiteResult(
        user_id=user_id,
        session_id=session_id,
        messages=[ElasticSuiteAnswer(
            message="Une réponse du chatbot",
            products=[]
        )]
    )

def __search_result(user_id, session_id):
    path = Path("data/temp.json").expanduser().resolve()
    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)

    return ElasticSuiteResult(
        user_id=user_id,
        session_id=session_id,
        messages=[ElasticSuiteAnswer(
            message="Voici une liste de produits :",
            products=data
        )]
    )
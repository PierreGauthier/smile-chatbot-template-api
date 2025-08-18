from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

import sys
import traceback
from datetime import datetime
from http import HTTPStatus

from fastapi import FastAPI, Request, Response, Body
from fastapi.responses import JSONResponse
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    BotFrameworkAdapter,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes

from routers import DefaultBot
from models import ApiChatRequest, ChatServiceResult, SetupServiceResult
from services import ChatService, DefaultRagChatService, ConversationalSearchSetupService

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

@router.post("/messages")
async def messages(chat_request: Request, BOT: Annotated[DefaultBot, Depends(DefaultBot)]) -> Response:
    
    if "application/json" in chat_request.headers["Content-Type"]:
        body = await chat_request.json()
    else:
        return Response(status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
    
    activity = Activity().deserialize(body)
    auth_header = chat_request.headers["Authorization"] if "Authorization" in chat_request.headers else ""

    response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
    if response:
        return JSONResponse(content=response.body, status_code=response.status)
    return Response(status_code=HTTPStatus.OK)

@router.post("/chat")
async def chat(
    service: Annotated[ChatService, Depends(DefaultRagChatService)],
    chat_request: ApiChatRequest = Body(...)
):
    ai_response: ChatServiceResult = service.invoke(
        input_message = chat_request.message, 
        session_id=chat_request.session_id,
        user_id=chat_request.user_id
    )
    return ai_response

@router.post("/setup")
async def chat(
    service: Annotated[ConversationalSearchSetupService, Depends(ConversationalSearchSetupService)]
):
    response: SetupServiceResult = service.setup()
    return response
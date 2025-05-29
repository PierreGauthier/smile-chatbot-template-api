from typing import Annotated
from fastapi import Depends

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount

from services import ChatService, DefaultRagChatService
from models import RagChatServiceResult

class DefaultBot(ActivityHandler):
    
    def __init__(self, chat_service: Annotated[ChatService, Depends(DefaultRagChatService)]):
        self.chat_service = chat_service
        
    async def on_message_activity(self, turn_context: TurnContext):
        conversation_id = turn_context.activity.conversation.id
        user_id = turn_context.activity.recipient.id
        message = turn_context.activity.text
        ai_response:RagChatServiceResult = self.chat_service.invoke(
            message = message, 
            session_id=conversation_id, 
            user_id=user_id
        )
        await turn_context.send_activity(ai_response.answer)

    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:                
                await turn_context.send_activity("Hello and welcome! How can I help you?")
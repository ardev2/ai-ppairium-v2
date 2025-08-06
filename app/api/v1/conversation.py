from fastapi import APIRouter
from models.conversation import MessageIn, MessageOut
from core.logging import logger

router = APIRouter()


@router.post("/start", response_model=MessageOut)
async def send_message(message: MessageIn):
    logger.info(message)
    message_out = MessageOut(
        conversation_id=message.conversation_id,
        content="Hello, how can I help you?",
        wait_response=True,
    )
    return message_out

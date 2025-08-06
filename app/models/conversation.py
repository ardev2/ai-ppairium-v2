from pydantic import BaseModel


class MessageIn(BaseModel):
    conversation_id: str
    content: str


class MessageOut(BaseModel):
    conversation_id: str
    content: str
    wait_response: bool

from pydantic import BaseModel, StrictStr, StrictInt, RootModel
from typing import List

class EmailComposeSchema(BaseModel):
    message: StrictStr

class ErrorEmailComposeSchema(BaseModel):
    error: StrictStr

class EmailDetailSchema(BaseModel):
    id: StrictInt
    sender: StrictStr
    recipients: List[StrictStr]
    subject: StrictStr
    body: StrictStr
    timestamp: StrictStr
    read: bool
    archived: bool
    
class ErrorEmailDetailsSchema(BaseModel):
    error: str

class EmailList(RootModel):
    root: List[EmailDetailSchema]

class ErrorEmailList(BaseModel):
    error: str


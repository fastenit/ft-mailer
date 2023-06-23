import json
from typing import List, Union
from pydantic import BaseModel, EmailStr


class MailToSend(BaseModel):
    
    subject: str
    html_string: str
    text_string: str = ""
    from_addr: EmailStr
    to: List[EmailStr] = []
    cc: List[EmailStr] = []
    bcc: List[EmailStr] = []
    
    


class MailerMessage(BaseModel):

    class Config:
        extra = "allow"

    recipients: List[EmailStr] = []
    mail_from: Union[EmailStr, None] = None
    mail_type: str
    lang: str
    hydration_data: dict = {}


class AccountActivationHydrationData(BaseModel):

    class Config:
        extra = "allow"

    account_id: str
    lang: str = "en"


class SnsNotification(BaseModel):

    Type: str
    MessageId: str
    TopicArn: str
    Subject: Union[str, None]
    Message: str
    Timestamp: str
    SignatureVersion: str
    Signature: str
    SigningCertUrl: str
    UnsubscribeUrl: str
    MessageAttributes: dict
    
    def get_mailer_message(self) -> MailerMessage:
        return MailerMessage.parse_obj(json.loads(self.Message))
    

class SnsRecord(BaseModel):
    
    EventSource: str
    EventVersion: str
    EventSubscriptionArn: str
    Sns: SnsNotification

class SnsEvent(BaseModel):

    class Config:
        extra = "forbid"
        
    Records: List[SnsRecord]
    
    
    


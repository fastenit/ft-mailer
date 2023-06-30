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

    mail_type: str
    override_lang_with: Union[str, None]
    hydration_data: dict = {}


class BaseHydrationData(BaseModel):

    class Config:
        extra = "allow"

    base_domain: str = "www.fasten.it"# This is the base url to use when sending the email should be like https://new.fsasten.it
    base_protocol: str = "https" # This is the base url to use when sending the email should be like https://new.fsasten.it
    

class AccountActivationHydrationData(BaseHydrationData):

    class Config:
        extra = "allow"

    account_id: str


class CompanyAssociationRequestHydrationData(BaseHydrationData):

    class Config:
        extra = "allow"

    requesting_account_id: str
    target_company_id: str


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
    
    
    


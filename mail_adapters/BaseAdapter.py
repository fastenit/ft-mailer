from services.data_service import DataService
from model.pydantic.models import MailToSend
from model.pydantic.models import SnsRecord, BaseHydrationData, MailerMessage
from typing import Iterable, Iterator
from jinja2 import Template, FileSystemLoader
from jinja2 import Environment, select_autoescape


class BaseAdapter():
 
    '''
    This is the base adapter for the email types to be sent with this mailer
    
    In order to create a new adapter, override two functions.
    
    self._get_mails_to_send_iterator() - Should return an iterable that returns a series of MailToSend objects
    self.message_hydration_data(self) -> BaseHydrationData() - Should return an Descendant of BaseHydrationData, specialized 
    
    
    '''
    _sns_record: SnsRecord = None
    _data_service: DataService = None
    _jinja_env = None
    _env = "DEV"
    
    def __init__(self, sns_record: SnsRecord, data_service: DataService, environment: str = "DEV"):
        
        self._sns_record: SnsRecord = sns_record
        self._data_service: DataService = data_service
        self._env: str = environment
        
        self._jinja_env = Environment(
            loader=FileSystemLoader("templates"),
            autoescape=select_autoescape()
        )

    @property
    def mail_type(self):
        mail_type = self._sns_record.Sns.get_mailer_message().mail_type
        return mail_type
        

    @property
    def override_lang_with(self):
        olw = self._sns_record.Sns.get_mailer_message().override_lang_with
        return olw

    @property
    def mailer_message(self) -> MailerMessage:
        mm = self._sns_record.Sns.get_mailer_message()
        return mm

    @property
    def mailer_message_hydration_data(self):
        return self.message_hydration_data()

        
    def mails_to_send(self):
        
        for mail_to_send in self._get_mails_to_send_iterator():

            # Mark the mails and prevent mail sendout when in STG and DEV Envs
            if self._env in ["STG", "DEV"]:
                mail_to_send.to = ["tech@fasten.it"]
                mail_to_send.bcc = []
                mail_to_send.cc = []
                mail_to_send.subject = f"[{self._env}] - " + mail_to_send.subject
            
            yield mail_to_send
        
    @property            
    def message_hydration_data(self) -> BaseHydrationData:
        raise Exception("BaseAdapter is an Abstract Class. Please override the __get_mails_to_send_iterator() -> Iterator[MailToSend] method")


    def _get_mails_to_send_iterator(self) -> Iterator[MailToSend]:
        raise Exception("BaseAdapter is an Abstract Class. Please override the __get_mails_to_send_iterator() -> Iterator[MailToSend] method")

    
from typing import Iterable
from mail_adapters.BaseAdapter import BaseAdapter
from model.pydantic.models import MailerMessage, SnsRecord, AccountActivationHydrationData
from model.sqlalchemy.Models import Account
from services.data_service import DataService
from jinja2 import Template, FileSystemLoader
from jinja2 import Environment, select_autoescape
from model.pydantic.models import MailToSend
import logging
import os
import sys

# Initialise logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(os.environ.get("LOG_LEVEL", "DEBUG").upper()))
logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(module)s "
    "%(process)s[%(thread)s] %(message)s",
)
logger.info("Logging at {} level".format(os.environ.get("LOG_LEVEL", "DEBUG")))


class CompanyAssociationRequestAdapter(BaseAdapter):

    '''
    This adapter composes the emails that must be sent to the
    "ADMINS" of a specific company when a new account is created and should be
    linked to an existing company
    '''

    account_id: str = None
    account: Account = None
    _jinja_env = None

    def __init__(self, sns_record: SnsRecord, data_service: DataService):
        super().__init__(sns_record, data_service=data_service)
        
        self._jinja_env = Environment(
            loader=FileSystemLoader("templates"),
            autoescape=select_autoescape()
        )
        
        self.message = self._sns_record.Sns.Message
        
        self._inflate_hydration_data()
        
    def mails_to_send(self) -> Iterable[MailToSend]:
        
        '''
        This function return an iterable with all the email that should be sent
        out in response to the SNS notification
        '''
        
        for recipient in self._get_recipients():
        
            mts = MailToSend(
                subject = self._produce_subject(),
                html_string = self._produce_html_message(),
                text_string = "",
                from_addr = self._get_mail_from(),
                to = [recipient]
            )
            
            yield mts
                    


    
    def _inflate_hydration_data(self):

        '''
        This function get the information in the sns message and inflate all the informations needed to send the email
        notification
        
        - recipients
        - language
        - subject string
            
        '''
        
        mailer_message_data: MailerMessage = self._sns_record.Sns.get_mailer_message()         
        mailer_hydration_data =  AccountActivationHydrationData.parse_obj(mailer_message_data.hydration_data)
                
        self.account = self._data_service.get_account_by_id(mailer_hydration_data.account_id)
        self.account_id = mailer_hydration_data.account_id
        self.mail_type = self._sns_record.Sns.get_mailer_message().mail_type
        self.pref_lang = self.account.language if self.account.language in ['it', 'en', 'uk', 'de'] else 'en'
        self.pref_lang = self.pref_lang if self.pref_lang != 'uk' else 'en'

        

    def _get_recipients(self):
        return [self.account.email]
                

    def _get_mail_from(self):
        return "noreply@fasten.it"

    def _produce_subject(self):
        if self.pref_lang == "it":
            return "Attiva il tuo account Fasten.it!"
        elif self.pref_lang == "de":
            return "[DE] Attiva il tuo account Fasten.it!"
        else:
            return "Activate your new Fasten.it account!"

    def _produce_html_message(self):
        mail_type = self._sns_record.Sns.get_mailer_message().mail_type
        pref_lang = self.account.language if self.account.language in ['it', 'en', 'uk', 'de'] else 'en'
        pref_lang = pref_lang if pref_lang != 'uk' else 'en'

        t = self._jinja_env.get_template(pref_lang + "/" + mail_type + ".html")

        hydration_data = {
            "base_url": "www.fasten.it",
            "base_protocol": "https",
            "user_name": self.account.name,
            "user_surname": self.account.surname,
            "activation_link_url": "https://new.fasten.it/ciccio/ciccio",
            "activation_code": self.account.auth_code
        }

        # Read the message files
        try:
            mime_message_text = t.render(hydration_data)
        except Exception as e:
            logger.info(e)
            mime_message_text = None
            logger.info(
                "Failed to read text message file. Did you upload %s?"
                % args["mail_type"]
            )

        if not mime_message_text:
            raise ValueError("Cannot continue without a text or html message file.")
    
        return mime_message_text

    def _produce_text_message(self):
        raise Exception("BaseAdapter is an Abstract Class. Please overload the _get_mail_from() method")

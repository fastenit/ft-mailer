from typing import Iterable
from mail_adapters.BaseAdapter import BaseAdapter
from model.pydantic.models import MailerMessage, SnsRecord, AccountActivationHydrationData, BaseHydrationData
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


class AccountActivationAdapter(BaseAdapter):

    account_id: str = None
    account: Account = None
        
                
    def _get_mails_to_send_iterator(self) -> Iterable[MailToSend]:
        
        '''
        This function return an iterable with all the email that should be sent
        out in response to the SNS notification
        '''
        
        hydration_data = self._get_data_to_inflate()
        
        for recipient in self._get_recipients(hydration_data):
        
            mts = MailToSend(
                subject = self._produce_subject(hydration_data),
                html_string = self._produce_html_message(hydration_data),
                text_string = "",
                from_addr = self._get_mail_from(),
                to = [recipient],
                cc = [],
                bcc = []
            )
            
            yield mts
                    
    @property    
    def message_hydration_data(self) -> AccountActivationHydrationData:
        return  AccountActivationHydrationData.parse_obj(self.mailer_message.hydration_data)
        
    
    def _get_data_to_inflate(self):

        '''
        This function get the information in the sns message and inflate all the informations needed to send the email
        notification            
        '''
                
        self.account = self._data_service.get_account_by_id(self.message_hydration_data.account_id)
        self.pref_lang = self.account.language if self.account.language in ['it', 'en', 'uk', 'de'] else 'en'
        self.pref_lang = self.pref_lang if self.pref_lang != 'uk' else 'en'
        
        if self.override_lang_with is not None:
            self.pref_lang = self.override_lang_with
            
        if self._env == "DEV":
            activation_base_url = f"{self.message_hydration_data.base_protocol}://onboarding-dev.fasten.it/activate/"
        elif self._env == "STG":
            activation_base_url = f"{self.message_hydration_data.base_protocol}://onboarding-stg.fasten.it/activate/"
        elif self._env == "PRD":
            activation_base_url = f"{self.message_hydration_data.base_protocol}://onboarding-prd.fasten.it/activate/"
        else:
            activation_base_url = f"{self.message_hydration_data.base_protocol}://onboarding-dev.fasten.it/activate/"

        hydration_data = {
            "base_domain": self.message_hydration_data.base_domain,
            "base_protocol": self.message_hydration_data.base_protocol,
            "account_email": self.account.email,
            "account_id": self.account.id,
            "user_name": self.account.name,
            "user_surname": self.account.surname,
            "activation_link_base_url": activation_base_url,
            "activation_code": self.account.auth_code
        }
        
        return hydration_data

    def _get_recipients(self, hydration_data: dict):
        return [hydration_data.get("account_email")]
                

    def _get_mail_from(self):
        return "noreply@fasten.it"

    def _produce_subject(self, hydration_data: dict):
        if self.pref_lang == "it":
            return "Attiva il tuo account Fasten.it!"
        elif self.pref_lang == "de":
            return "Attiva il tuo account Fasten.it!"
        else:
            return "Activate your new Fasten.it account!"

    def _produce_html_message(self, hydration_data: dict):
        # pref_lang = self.account.language if self.account.language in ['it', 'en', 'uk', 'de'] else 'en'
        # pref_lang = pref_lang if pref_lang != 'uk' else 'en'

        t = self._jinja_env.get_template(self.pref_lang + "/" + self.mail_type + ".html")

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

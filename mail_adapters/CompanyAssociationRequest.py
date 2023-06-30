from typing import Iterable
from mail_adapters.BaseAdapter import BaseAdapter
from model.pydantic.models import MailerMessage, SnsRecord, CompanyAssociationRequestHydrationData, BaseHydrationData
from model.sqlalchemy.Models import Account, Utente
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

    account_id: str = None
    account: Account = None
    
    _requesting_account: Account = None 
    _target_company: Utente = None 
        
    def _get_mails_to_send_iterator(self) -> Iterable[MailToSend]:
        
        '''
        This function return an iterable with all the email that should be sent
        out in response to the SNS notification
        '''
        
        self._requesting_account = self._data_service.get_account_by_id(self.message_hydration_data.requesting_account_id)
        self._target_company = self._data_service.get_company_by_id(self.message_hydration_data.target_company_id)

        for managing_account in self._target_company.accounts:
            
            hydration_data = {
                "tgt_user_name": managing_account.account.name,
                "tgt_user_surname": managing_account.account.surname,
                "req_user_name": self._requesting_account.name,
                "req_user_surname": self._requesting_account.surname,
                "req_user_email": self._requesting_account.email,
                "tgt_company_name": self._target_company.nome
            }
            
            ln = managing_account.account.language if managing_account.account.language in ["it", "en", "de"] else "en"
            
            mts = MailToSend(
                subject = self._produce_subject(ln),
                html_string = self._produce_html_message(hydration_data, ln),
                text_string = "",
                from_addr = self._get_mail_from(),
                to = [managing_account.account.email],
                cc = [],
                bcc = []
            )
            
            yield mts
                    
    @property    
    def message_hydration_data(self) -> CompanyAssociationRequestHydrationData:
        return  CompanyAssociationRequestHydrationData.parse_obj(self.mailer_message.hydration_data)
    
    @property
    def language(self):
        if self.override_lang_with:
            return self.override_lang_with
        
        return self._requesting_account.language
    
    def _get_recipients(self, hydration_data: dict):
        return [hydration_data.get("account_email")]
                

    def _get_mail_from(self):
        return "noreply@fasten.it"

    def _produce_subject(self, language):
        if language == "it":
            return f"{self._requesting_account.name} {self._requesting_account.surname} ha richiesto di essere associato alla tua azienda su Fasten.it"
        elif language == "de":
            return f"[DE] {self._requesting_account.name} {self._requesting_account.surname} ha richiesto di essere associato alla tua azienda su Fasten.it"
        else:
            return f"{self._requesting_account.name} {self._requesting_account.surname} wants to be connected to your company on Fasten.it"

    def _produce_html_message(self, hydration_data: dict = {}, language = "en"):
        # pref_lang = self.account.language if self.account.language in ['it', 'en', 'uk', 'de'] else 'en'
        # pref_lang = pref_lang if pref_lang != 'uk' else 'en'

        t = self._jinja_env.get_template(language + "/" + self.mail_type + ".html")

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

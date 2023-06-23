from model.pydantic.models import SnsRecord
from services.data_service import DataService

class BaseAdapter():
 
    '''
    This is the base adapter for the email types to be sent with this mailer
    '''
    _sns_record: SnsRecord = None
    _data_service: DataService = None
    
    def __init__(self, sns_record: SnsRecord, data_service: DataService):
        self._sns_record: SnsRecord = sns_record
        self._data_service: DataService = data_service
        
    def mail_to_send(self):
        raise Exception("BaseAdapter is an Abstract Class. Please overload the mail_to_sen() method")
                
    def _inflate_hydration_data(self):
        raise Exception("BaseAdapter is an Abstract Class. Please overload the _inflate_hydration_data() method")

    def _get_hydration_data(self):
        raise Exception("BaseAdapter is an Abstract Class. Please overload the _get_hydration_data() method")

    def _get_recipients(self):
        raise Exception("BaseAdapter is an Abstract Class. Please overload the _get_recipient_data() method")

    def _get_recipients(self):
        raise Exception("BaseAdapter is an Abstract Class. Please overload the _get_recipient_data() method")

    def _get_mail_from(self):
        raise Exception("BaseAdapter is an Abstract Class. Please overload the _get_mail_from() method")

    def _produce_html_message(self):
        raise Exception("BaseAdapter is an Abstract Class. Please overload the _get_mail_from() method")

    def _produce_text_message(self):
        raise Exception("BaseAdapter is an Abstract Class. Please overload the _get_mail_from() method")

    def _produce_subject_message(self):
        raise Exception("BaseAdapter is an Abstract Class. Please overload the _get_mail_from() method")
    
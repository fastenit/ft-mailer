from __future__ import print_function

import json
import os
import sys
import logging
import configparser

from model.pydantic.models import SnsEvent, SnsRecord
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from services.data_service import DataService

from mail_adapters.AccountActivation import AccountActivationAdapter
from mail_adapters.CompanyAssociationRequest import CompanyAssociationRequestAdapter

import boto3
import concurrent.futures

# Get Lambda environment variables
region = os.environ.get("REGION", "eu-west-1")
max_threads = int(os.environ.get("MAX_THREADS", 1))
ses_mailer_region = os.environ.get("SES_MAILER_REGION", "eu-west-1")
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
environment = os.environ.get("ENV", "STG").upper()

mysql_hostname = os.environ.get("MYSQL_HOSTNAME", "192.168.1.1")
mysql_port = os.environ.get("MYSQL_PORT", 3306)
mysql_username = os.environ.get("MYSQL_USERNAME", "root")
mysql_password = os.environ.get("MYSQL_PASSWORD", "bulunat")
mysql_db = os.environ.get("MYSQL_DB", "fasten")

# Initialise logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(log_level))
logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(module)s "
    "%(process)s[%(thread)s] %(message)s",
)
logger.info("Logging at {} level".format(log_level))

config = configparser.ConfigParser()
config.read("ENV_" + environment + '.ini')

print(config.sections())

# Initialise clients
boto3.setup_default_session()

ses = boto3.client("ses", region_name=ses_mailer_region)

def mime_email(
    subject,
    from_address,
    to_address,
    cc_address=[],
    bcc_address=[],
    text_message=None,
    html_message=None,
):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = ", ". join(to_address)
    if cc_address:
        msg["CC"] = ", ". join(cc_address)
    if bcc_address:
        msg["BCC"] = ", ". join(bcc_address)
    if text_message:
        msg.attach(MIMEText(text_message, "text"))
    if html_message:
        msg.attach(MIMEText(html_message, "html"))

    return msg.as_string()


def send_mail(from_address, 
              to_address, 
              cc_address, 
              bcc_address, 
              subject, 
              html_message, 
              text_message = None):
    try:
        response = ses.send_email(
            Source=from_address, 
            Destination={
                    "ToAddresses": to_address,
                    "CcAddresses": cc_address,
                    "BccAddresses": bcc_address
                },
            Message={
                "Subject": {
                    "Data": subject,
                    "Charset": "UTF-8"
                },
                "Body": {
                    "Html": {
                        "Data": html_message,
                        "Charset": "UTF-8"
                    },
                    "Text": {
                        "Data": text_message,
                        "Charset": "UTF-8"
                    }                    
                }
            }
        )
        
        if not isinstance(response, dict):  # log failed requests only
            logger.error(
                "Error sending to: %s, %s" % (to_address, response)
            )
    except Exception as e:
        logger.error(f"Error sending to: {to_address}. Exception: {e}")


def get_adapter_class(sns_record: SnsRecord):

    mailer_message = sns_record.Sns.get_mailer_message()
        
    if mailer_message.mail_type == "account_activation":
        return AccountActivationAdapter

    if mailer_message.mail_type == "account_company_association_request":
        return CompanyAssociationRequestAdapter

    raise Exception(f"Non c'è un adattatore per l'invio di questo tipo di email {mailer_message.mail_type}")    


def lambda_handler(event, context):

    data_service = DataService(mysql_hostname, mysql_port, mysql_username, mysql_password, mysql_db)

    e = concurrent.futures.ThreadPoolExecutor(max_workers=max_threads)

    try:
        sns_event = SnsEvent.parse_obj(event)

        for record in sns_event.Records:
            
            adptr_cls = get_adapter_class(record)
            adapter = adptr_cls(record, data_service, environment)
            
            for mail in adapter.mails_to_send():
                e.submit(
                    send_mail, mail.from_addr, mail.to, mail.cc, mail.bcc, mail.subject, mail.html_string, mail.text_string   
                )
        
        e.shutdown()
                            
    except Exception as e:
        logger.exception("Aborting... " + str(e))
        raise e


# This is used in order to test locally the lambda

if __name__ == "__main__":
    json_content = json.loads(open("event_association.json", "r").read())
    lambda_handler(json_content, None)

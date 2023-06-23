from __future__ import print_function

import json
import os
import sys
import logging

from model.pydantic.models import SnsEvent, SnsRecord
from time import strftime, gmtime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template, FileSystemLoader
from jinja2 import Environment, select_autoescape
from services.data_service import DataService

from mail_adapters.AccountActivation import AccountActivationAdapter

import boto3
import concurrent.futures

__author__ = "DWP DataWorks"
__date__ = "14/05/2019"
__version__ = "1.1"

# Get Lambda environment variables
region = os.environ.get("REGION", "eu-west-1")
max_threads = int(os.environ.get("MAX_THREADS", 1))
from_domain = os.environ.get("SENDING_DOMAIN", "fasten.it")

if "SES_MAILER_REGION" in os.environ:
    ses_mailer_region = os.environ["SES_MAILER_REGION"]
else:
    ses_mailer_region = "eu-west-1"

# Initialise logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(os.environ.get("LOG_LEVEL", "DEBUG").upper()))
logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s %(levelname)s %(module)s "
    "%(process)s[%(thread)s] %(message)s",
)
logger.info("Logging at {} level".format(os.environ.get("LOG_LEVEL", "DEBUG")))

# Initialise clients
boto3.setup_default_session(profile_name=os.environ.get("AWS_PROFILE", "fasten"))

ses = boto3.client(
    "ses", region_name=ses_mailer_region if ses_mailer_region else region
)
mime_message_text = ""
mime_message_html = ""


def current_time():
    return strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())


def mime_email(
    subject,
    from_address,
    to_address,
    cc_address=None,
    bcc_address=None,
    text_message=None,
    html_message=None,
):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = to_address
    if cc_address:
        msg["CC"] = cc_address
    if bcc_address:
        msg["BCC"] = bcc_address
    if text_message:
        msg.attach(MIMEText(text_message, "html"))
    if html_message:
        msg.attach(MIMEText(html_message, "html"))

    return msg.as_string()


def send_mail(from_address, to_address, cc_address, bcc_address, message):
    try:
        dest = [to_address]
        dest.append(cc_address) if cc_address is not None else None
        dest.append(bcc_address) if bcc_address is not None else None
        response = ses.send_raw_email(
            Source=from_address, Destinations=dest, RawMessage={"Data": message}
        )
        if not isinstance(response, dict):  # log failed requests only
            logger.error(
                "%s, Error sending to: %s, %s" % (current_time(), to_address, response)
            )
    except Exception as e:
        logger.error(f"Error sending to: {to_address}. Exception: {e}")


def get_parameters(event):
    print(event)
    message = json.loads(event["Records"][0]["Sns"]["Message"])

    return message


def get_adapter_class(sns_record: SnsRecord):

    mailer_message = sns_record.Sns.get_mailer_message()
        
    if mailer_message.mail_type == "account_activation":
        return AccountActivationAdapter

    raise Exception(f"Non c'è un adattatore per l'invio di questo tipo di email {mailer_message.mail_type}")    


def lambda_handler(event, context):

    env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape()
    )
    
    data_service = DataService("192.168.1.1", 3306, "root", "bulunat", "fasten")

    e = concurrent.futures.ThreadPoolExecutor(max_workers=max_threads)

    
    # global mime_message_text
    # global mime_message_html

    try:
        sns_event = SnsEvent.parse_obj(event)

        for record in sns_event.Records:
            
            adptr_cls = get_adapter_class(record)
            adapter = adptr_cls(record, data_service)
            
            for mail in adapter.mails_to_send():
                message = mime_email(
                    mail.subject,
                    mail.from_addr,
                    mail.to,
                    [],
                    [],
                    mail.html_string
                )
                e.submit(
                    send_mail, mail.from_addr, mail.to, None, None, message
                )
        
        e.shutdown()
                            

        # args = get_parameters(event)

        # if args["recipients"]:
        #     recipients = args["recipients"]
        # else:
        #     recipients = []

        # if args["lang"]:
        #     lang = args["lang"]
        # else:
        #     lang = "en" # Defaults to EN

        # mail_type = args["mail_type"]

        # t = env.get_template(lang + "/" + mail_type + ".html")
        # # Read the message files
        # try:
        #     mime_message_text = t.render(args["hydration_data"])
        # except Exception as e:
        #     logger.info(e)
        #     mime_message_text = None
        #     logger.info(
        #         "Failed to read text message file. Did you upload %s?"
        #         % args["mail_type"]
        #     )

        # if not mime_message_text:
        #     raise ValueError("Cannot continue without a text or html message file.")

        # Send in parallel using several threads
        # for recipient in recipients:
        #     from_address = args["mail_from"]
        #     to_address = recipient

        #     subject = "Benvenuto, ora attiva il tuo account Fasten.it"

        #     message = mime_email(
        #         subject,
        #         from_address,
        #         to_address,
        #         [],
        #         [],
        #         mime_message_text
        #     )
        #     e.submit(
        #         send_mail, from_address, to_address, None, None, message
        #     )
        # e.shutdown()
    except Exception as e:
        logger.exception("Aborting... " + str(e))
        raise e


if __name__ == "__main__":
    json_content = json.loads(open("event.json", "r").read())
    lambda_handler(json_content, None)

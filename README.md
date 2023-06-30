# ft-mailer - Transactional Mailer for Fasten.it

AWS Lambda application to send emails via AWS SES using information recieved from AWS SNS notification

## Usage

This lambda is intended to be invoked by a sns notification comimng from a specific Topic and receives a payload
containing the following information.

* The type of transactional email that is to be sent
* The fallback language that the email should be sent over, if the handler is not able to determine a language
* Some metadata that is needed by the  Mailing Adapter for the specific type of email to inflate the email/text/subject 

### Templates

The lambda uses templates, which are deployed from the `aws-common-infrastructure` repository as well.

### Sending emails

In order to send an email from this lambda, you can invoke it with a payload that looks like an sns message:

    {
      "Records": [
        {
          "Sns": {
            "Message": {
            ...
            }
          }
        }
      ]
    }

The message object should have the following properties:

* `recipients` -> A `;` separated list of email recipients
* `mailing_list` -> A mailing list name for the email to go to
* `bucket` -> The S3 bucket name containing the email templates
* `plain_text_template` -> The name of the plain text email template file from s3
* `template_variables` -> The variables as a key/value pair dictionary that with be inserted in to the template
* `html_template` -> The name of the html email template file from s3
* `from_local_part` -> The name of the from field

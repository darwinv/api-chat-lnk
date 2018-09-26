import boto3
from botocore.exceptions import ClientError
from django.template.loader import get_template
from django.template import Context


class BasicEmailAmazon(object):

    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    sender = "team@pympack.com.pe"
    # The character encoding for the email.


    def __init__(self,subject,to,template):
        # Asunto del Email
        self.subject = subject
        self.to = to
        self.charset = "UTF-8"
        # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
        self.region = "us-east-1"
        self.template_html = template +'.html'
        self.template_txt = template +'.txt'

    def sendmail(self, args):
        """Metodo para enviar correos por Amazon."""
        # Create a new SES resource and specify a region.
        client = boto3.client('ses', region_name=self.region)
        d = (args)
        #
        html = get_template(self.template_html)
        txt = get_template(self.template_txt)
        html_content = html.render(d)
        txt_content = txt.render(d)
        
        # Try to send the email.
        try:
            response = client.send_email(
                    Destination={
                        'ToAddresses': [
                            self.to,
                        ],
                    },
                    Message={
                        'Body': {
                            'Html': {
                                'Charset': self.charset,
                                'Data': html_content,
                            },
                            'Text': {
                                'Charset': self.charset,
                                'Data': txt_content,
                            },
                        },
                        'Subject': {
                            'Charset': self.charset,
                            'Data': self.subject,
                        },
                    },
                    Source=BasicEmailAmazon.sender,
                    # If you are not using a configuration set, comment or delete the
                    # following line
                    #ConfigurationSetName=CONFIGURATION_SET,
                )
            # Display an error if something goes wrong.
        except ClientError as e:
            return (e.response['Error']['Message'])
        else:
            # print("Email sent! Message ID:"),
            return (response['ResponseMetadata']['RequestId'])

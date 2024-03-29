import os
import smtplib
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mimetypes import guess_type, read_mime_types

from zemailer.core.backends import Gmail
from zemailer.core.exceptions import NoServerError

# from zemailer.settings import configuration
# from zemailer.utils.template_loader import render_template


class TemplateMixin:
    suject = None
    html_body = None
    email_body = None


class SendEmail:
    """Send an email using a server

    Parameters
    ----------

    - sender the email sending the message
    - receiver the email or emails receiving the message
    - subject of the message that you are sending 
    - server is the backend used to send the email(s)

    Optional: `attachment` corresponds to the path of the object
    that you want to attach to the email
    """
    server = Gmail

    def __init__(self, sender, receiver, subject,
                 email_body=None, html_body=None, **kwargs):
        if self.server:
            if callable(self.server):
                # defaults = configuration.SERVER_CONFIG['default']
                # user = defaults['user']
                # password = defaults['password']
                # Klass = self.server(user, password)
                Klass = self.server('inglish.contact@gmail.com', 'czvbekcrgzwswabk')
            else:
                raise NoServerError(
                    f"Server is not a callable. Received {self.server}")
        else:
            raise NoServerError(
                "Server was not provided. Did you forget to register a server?")

        # Create a MIME object
        message = MIMEMultipart('alternative')
        message['From'] = sender
        message['To'] = receiver
        message['Subject'] = subject

        # Create MIME text objects
        # text = MIMEText('This is a test', 'plain')
        # html = MIMEText('<html><body>This is a test</body></html>', 'html')

        text = MIMEText(email_body, 'text')
        message.attach(text)

        if html_body is not None:
            html = MIMEText(html_body, 'html')
            message.attach(html)

        # Attachment - attach if any
        if 'attachment' in kwargs:
            message.attach(kwargs['attachment'])

        # ..Send email
        try:
            Klass.smtp_connection.sendmail(sender, receiver, message.as_string())
        except smtplib.SMTPException as e:
            print(e)
        finally:
            Klass.smtp_connection.close()


class SendEmailWithAttachment(SendEmail):
    def __init__(self, sender, receiver, subject, file_path, **kwargs):
        attachment = self.create_attachment(file_path)
        super().__init__(sender, receiver, subject, attachment=attachment)

    def create_attachment(self, path):
        """Create an attachment using a local path
        """
        content = open(path, 'rb')
        # mime_type = guess_type(path)
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(content.read())
        content.close()
        # Encode in Base64
        encode_base64(attachment)
        # Get the file's name
        filename = os.path.basename(path)
        attachment.add_header('Content-Disposition',
                              f"attachment; filename= {filename}")
        return attachment

    def create_attachments(self, paths):
        if not isinstance(paths, (list, tuple)):
            raise TypeError()

        attachments = []

        for path in paths:
            attachments.append(self.create_attachment(path))

        return attachments


class SendEmailFromTemplate(SendEmail):
    def __init__(self, sender: str, receiver: str, subject: str, email_template: str, html_template: str, context: dict):
        email_body = render_template(email_template, context=context)
        html_body = render_template(html_template, context=context)
        super().__init__(sender, receiver, subject,
                         email_body=email_body, html_body=html_body)

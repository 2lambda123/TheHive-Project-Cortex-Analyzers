#!/usr/bin/env python
# encoding: utf-8

from cortexutils.responder import Responder
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mailer(Responder):
    def __init__(self):
        Responder.__init__(self)
        self.smtp_host = self.get_param(
            'config.smtp_host', 'localhost')
        self.smtp_port = self.get_param(
            'config.smtp_port', '25')
        self.mail_from = self.get_param(
            'config.from', None, 'Missing sender email address')
        self.smtp_auth = self.get_param(
            'config.smtpauth', False)
        self.username = self.get_param(
            'config.username', None)
        self.password = self.get_param(
            'config.password', None)

    def run(self):
        Responder.run(self)

        title = self.get_param('data.title', None, 'title is missing')
        description = self.get_param('data.description', None, 'description is missing')
        mail_to = None
        if self.data_type == 'thehive:case':
            # Search recipient address in tags
            tags = self.get_param('data.tags', None, 'recipient address not found in tags')
            mail_tags = [t[5:] for t in tags if t.startswith('mail:')]
            if mail_tags:
                mail_to = mail_tags.pop()
            else:
                self.error('recipient address not found in observables')
        elif self.data_type == 'thehive:alert':
            # Search recipient address in artifacts
            artifacts = self.get_param('data.artifacts', None, 'recipient address not found in observables')
            mail_artifacts = [a['data'] for a in artifacts if a.get('dataType') == 'mail' and 'data' in a]
            if mail_artifacts:
                mail_to = mail_artifacts.pop()
            else:
                self.error('recipient address not found in observables')
        else:
            self.error('Invalid dataType')

        msg = MIMEMultipart()
        msg['Subject'] = title
        msg['From'] = self.mail_from
        msg['To'] = mail_to
        msg.attach(MIMEText(description, 'plain'))

        s = smtplib.SMTP(self.smtp_host, self.smtp_port)
        if self.smtpauth:
            s.ehlo()
            s.starttls()
            s.login(self.username, self.password)
        s.sendmail(self.mail_from, mail_to.split(','), msg.as_string())
        s.quit()
        self.report({'message': 'message sent'})

    def operations(self, raw):
        return [self.build_operation('AddTagToCase', tag='mail sent')]


if __name__ == '__main__':
    Mailer().run()

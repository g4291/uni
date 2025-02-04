#!/usr/bin/env python3
"""
uni.services.mail

e-mail service
"""

from __future__ import annotations
import smtplib
import ssl
from email.message import EmailMessage
from typing import List

from ..logger import core_logger
from ..default import UniDefault
from ..exceptions import ServerError


# logger
logger = core_logger().getChild("mail")

class MailService(UniDefault):
    """ MailService class"""
    def __init__(self) -> None:
        try:
            # ssl / starttls context
            if self.config.mail.ssl or self.config.mail.tls:
                self._context = ssl.create_default_context()
            
            # ssl / tls
            if self.config.mail.ssl:
                self.server = smtplib.SMTP_SSL(
                    host=self.config.mail.smtp_server_address,
                    port=self.config.mail.smtp_server_port,  # SSL typically uses port 465
                    context=self._context
                )
            elif self.config.mail.tls:
                self.server = smtplib.SMTP(
                    host=self.config.mail.smtp_server_address,
                    port=self.config.mail.smtp_server_port  # STARTTLS typically uses port 587
                )
                self.server.starttls(context=self._context)
            else:
                self.server = smtplib.SMTP(
                    host=self.config.mail.smtp_server_address,
                    port=self.config.mail.smtp_server_port
                )
        except Exception as e:
            raise ServerError(f"error creating Mail service instance, exception: {e}") from None

        # login
        self._login()

    def _login(self) -> bool:
        """ handle mail login"""
        try:
            self.server.login(self.config.mail.username, self.config.mail.password)
        except Exception:
            raise ServerError("unable to create Mail service instance") from None
        return True

    def send(self, recipients: List[str], subject: str, message: str, sender: str, _raise: bool = False) -> None:
        for r in recipients:
            try:
                # only log email in debug
                if self.config.mail.debug:
                    logger.info(f"recipient: {r}, {message}")
                    continue 

                # Create the email message
                msg = EmailMessage()
                msg.set_content(message, subtype='html')
                msg['Subject'] = subject
                if sender: msg['From'] = sender
                else: msg['From'] = self.config.mail.sender
                msg['To'] = r
                msg.set_charset('utf-8')

                # Send the email
                self.server.send_message(msg)
                logger.info(f'Sent email with subject {subject} to {r}')
                
            except smtplib.SMTPException as e:
                logger.error(f"SMTP Error while sending email to {r}: {e}")
                if _raise:
                    raise ServerError(f"error sending email, exception: {e}") from None
            except Exception as e:
                logger.error(f"Unexpected Error while sending email to {r}: {e}")
                if _raise:
                    raise ServerError(f"error sending email, exception: {e}") from None
    

if __name__ == "__main__": exit()
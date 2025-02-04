#!/usr/bin/env python3

"""
uni.modules.notification.model

notification database model
"""

from __future__ import annotations
import json
from typing import Any, List, Optional
import uuid
from pydantic import BaseModel, Field, PrivateAttr

from ...database import database_factory
from ...database.model import DatabaseModel, DatabaseUpdateModel
from ...services.mail import MailService
from ..file.model import db_File
from ..user.model import db_User


class BaseNotification(BaseModel):
    """ base notification model, email validation"""
    user_id: uuid.UUID
    name: str
    detail: Any
    text: str
    read: bool = False
    files: List[db_File] = Field(default_factory=list)
    email: bool = True

class Notification(DatabaseModel, BaseNotification):
    """ base notification db model"""
    
    def send_to_mail(self) -> None:
        """ sends notification to email """
        recipient_user = database_factory().get_one(self.user_id, db_User)
        if not recipient_user: return None
        
        #sender email
        sender_email = ""
        if self.created.user_id:
            try: sender_email = database_factory().get_one(self.created.user_id, db_User).email
            except: pass
                    
        # notification detail
        detail = ""
        try: detail = json.dumps(self.detail, indent=4)
        except: detail = str(self.detail)
            
        
        subject = f"Notification: {self.name}"
        msg = f"{self.text} \n\ndetail: \n{detail}"
        
        if len(self.files) > 0:
            msg += "\n\nfiles:\n"
            for f in self.files:
                link = f.get_full_public_link()
                if link == "": continue
                msg += link + "\n"
        
        MailService().send([recipient_user.email], subject, msg, sender_email)

class db_Notification(Notification):
    """ database model """
    _index: List[str] = PrivateAttr(default=["user_id", "read"])

class CreateNotification(BaseNotification):
    """ update model """

class UpdateNotification(DatabaseUpdateModel):
    """ update model """
    read: Optional[bool] = None


if __name__ == "__main__": exit()
from mongoengine import Document, StringField, ReferenceField, DateTimeField
from datetime import datetime, timezone
from models.user import User

class History(Document):
    user_id = ReferenceField(User, required=True)
    image = StringField(required=True)
    text = StringField(required=True)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    meta = {'collection': 'histories'}

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super(History, self).save(*args, **kwargs)
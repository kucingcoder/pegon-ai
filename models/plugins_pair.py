from mongoengine import Document, ReferenceField, StringField, DateTimeField
from datetime import datetime, timedelta, timezone
from models.user import User

class PluginsPair(Document):
    user_id = ReferenceField(User, default=None)
    device = StringField(required=True, max_length=255)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    expired_at = DateTimeField(default=lambda: datetime.now(timezone.utc) + timedelta(seconds=5))
    
    meta = {'collection': 'plugins_pairs'}

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super(PluginsPair, self).save(*args, **kwargs)
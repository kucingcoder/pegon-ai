from mongoengine import Document, ReferenceField, DateTimeField
from datetime import datetime, timezone
from models.user import User

class PluginsPair(Document):
    user_id = ReferenceField(User, default=None)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    meta = {'collection': 'plugins_pairs'}

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super(PluginsPair, self).save(*args, **kwargs)
from mongoengine import Document,ReferenceField, StringField, DateTimeField
from datetime import datetime, timezone
from models.admin import Admin

class Tutorial(Document):
    admin_id = ReferenceField(Admin, required=True)
    name = StringField(required=True, unique=True, max_length=64)
    thumbnail = StringField(required=True)
    description = StringField(required=True)
    link = StringField(required=True)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {'collection': 'tutorials'}

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super(Tutorial, self).save(*args, **kwargs)
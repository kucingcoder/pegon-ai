from mongoengine import Document, StringField, DateTimeField
from datetime import datetime, timezone

class Tutorial(Document):
    name = StringField(required=True, unique=True)
    thumbnail = StringField(required=True)
    description = StringField(required=True)
    link = StringField(required=True)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {'collection': 'tutorials'}

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super(Tutorial, self).save(*args, **kwargs)
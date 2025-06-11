from mongoengine import Document, StringField, DateTimeField
from datetime import datetime, timezone

class Admin(Document):
    username = StringField(required=True, max_length=64)
    password = StringField(required=True, max_length=32)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
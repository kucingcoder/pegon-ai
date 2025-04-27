from mongoengine import Document, StringField, DateTimeField
from datetime import datetime

class article(Document):
    name = StringField(required=True, unique=True)
    writer = StringField(required=True)
    file = StringField(required=True)
    created_at = DateTimeField(default=datetime.now(datetime.timezone.utc))
    updated_at = DateTimeField(default=datetime.now(datetime.timezone.utc))
    
    meta = {'collection': 'articles'}
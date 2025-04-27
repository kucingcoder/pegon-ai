from mongoengine import Document, StringField, ReferenceField, DateTimeField
from datetime import datetime
from models.user import User

class History(Document):
    user_id = ReferenceField(User, required=True)
    image = StringField(required=True)
    text = StringField(required=True)
    created_at = DateTimeField(default=datetime.now(datetime.timezone.utc))
    updated_at = DateTimeField(default=datetime.now(datetime.timezone.utc))
    
    meta = {'collection': 'histories'}
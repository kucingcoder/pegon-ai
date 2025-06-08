from mongoengine import Document, StringField, ReferenceField, DateTimeField
from datetime import datetime, timezone
from models.user import User

class LogActivity(Document):
    user_id = ReferenceField(User, required=True)
    activity = StringField(required=True)
    device = StringField(required=True)
    timestamp = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    meta = {'collection': 'log_activity'}
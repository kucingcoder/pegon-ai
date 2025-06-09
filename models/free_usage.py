from mongoengine import Document, ReferenceField, DateField
from datetime import datetime, timezone
from models.user import User

class FreeUsage(Document):
    user_id = ReferenceField(User, required=True)
    created_at = DateField(default=lambda: datetime.now(timezone.utc).date())
    
    meta = {'collection': 'free_usage'}
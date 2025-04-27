from mongoengine import Document, StringField, ReferenceField, DateTimeField
from datetime import datetime
from models.user import User

class Otp(Document):
    user_id = ReferenceField(User, required=True)
    code = StringField(required=True)
    expired = DateTimeField(required=True)
    status = StringField(default='active', choices=('active', 'expired'))
    created_at = DateTimeField(default=datetime.now(datetime.timezone.utc))
    updated_at = DateTimeField(default=datetime.now(datetime.timezone.utc))
    
    meta = {'collection': 'otps'}
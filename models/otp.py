from mongoengine import Document, StringField, ReferenceField, DateTimeField
from datetime import datetime, timezone
from models.user import User

class Otp(Document):
    user_id = ReferenceField(User, required=True)
    code = StringField(required=True)
    expired = DateTimeField(required=True)
    status = StringField(default='active', choices=('active', 'expired'))
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    meta = {'collection': 'otps'}

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super(Otp, self).save(*args, **kwargs)
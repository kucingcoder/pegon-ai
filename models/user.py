from mongoengine import Document, StringField, DateTimeField
from datetime import datetime, timezone

class User(Document):
    name = StringField(required=True, unique=True, max_length=64)
    sex = StringField(required=True, choices=('male', 'female'))
    date_of_birth = DateTimeField(required=True)
    phone_code = StringField(required=True)
    phone_number = StringField(required=True, unique=True, max_length=16)
    api_key = StringField(required=True, unique=True)
    status = StringField(default='active', choices=('active', 'suspend'))
    role = StringField(default='user', choices=('user', 'admin'))
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    meta = {'collection': 'users'}

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super(User, self).save(*args, **kwargs)
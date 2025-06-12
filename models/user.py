from mongoengine import Document, StringField, DateTimeField, DateField
from datetime import datetime, timedelta, timezone

class User(Document):
    name = StringField(required=True, max_length=64)
    sex = StringField(choices=('male', 'female', 'other'))
    date_of_birth = DateTimeField()
    
    phone_code = StringField(default=None)
    phone_number = StringField(default=None, unique=True, sparse=True, max_length=16)
    email = StringField(default=None, unique=True, sparse=True, max_length=254)
    
    api_key = StringField(required=True, unique=True)
    status = StringField(default='active', choices=('active', 'suspend'))
    category = StringField(default='free', choices=('free', 'pro'))
    
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    expired_at = DateField(default=lambda: datetime.now(timezone.utc).date() + timedelta(days=30))

    meta = {'collection': 'users'}

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super(User, self).save(*args, **kwargs)

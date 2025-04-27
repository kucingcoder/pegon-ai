from mongoengine import Document, StringField, DateTimeField
from datetime import datetime

class user(Document):
    name = StringField(required=True, unique=True)
    sex = StringField(required=True, choices=('male', 'female'))
    date_of_birth = DateTimeField(required=True)
    phone_code = StringField(required=True)
    phone_number = StringField(required=True, unique=True)
    api_key = StringField(required=True, unique=True)
    status = StringField(default='active', choices=('active', 'suspend'))
    role = StringField(default='user', choices=('user', 'admin'))
    created_at = DateTimeField(default=datetime.now(datetime.timezone.utc))
    updated_at = DateTimeField(default=datetime.now(datetime.timezone.utc))
    
    meta = {'collection': 'users'}
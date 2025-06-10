from mongoengine import Document, StringField, IntField, ReferenceField, DateTimeField
from datetime import datetime, timezone
from models.user import User

class Payment(Document):
    user_id = ReferenceField(User, required=True)
    product = StringField(required=True)
    price = IntField(required=True)
    status = StringField(default='pending', choices=('pending', 'settlement', 'cancel'))
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    meta = {'collection': 'payments'}

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super(Payment, self).save(*args, **kwargs)
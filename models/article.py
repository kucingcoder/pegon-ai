from mongoengine import Document, StringField, DateTimeField
from datetime import datetime, timezone

class Article(Document):
    name = StringField(required=True, unique=True)
    writer = StringField(required=True)
    file = StringField(required=True)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))

    meta = {'collection': 'articles'}

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super(Article, self).save(*args, **kwargs)
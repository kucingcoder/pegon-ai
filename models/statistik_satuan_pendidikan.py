from datetime import datetime, timezone
from mongoengine import Document, StringField, DateTimeField, IntField

class StatistikSatuanPendidikan(Document):
    year = StringField(required=True, unique=True)
    kbSederajat = IntField(required=True)
    tkSederajat = IntField(required=True)
    tpa = IntField(required=True)
    sps = IntField(required=True)
    sdSederajat = IntField(required=True)
    smpSederajat = IntField(required=True)
    smaSederajat = IntField(required=True)
    smkSederajat = IntField(required=True)
    slb = IntField(required=True)
    dikmas = IntField(required=True)
    total = IntField(required=True)
    created_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(default=lambda: datetime.now(timezone.utc))
    
    meta = {'collection': 'statistik_satuan_pendidikan'}

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now(timezone.utc)
        return super(StatistikSatuanPendidikan, self).save(*args, **kwargs)
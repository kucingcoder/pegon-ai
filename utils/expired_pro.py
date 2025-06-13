import datetime
from models.user import User
def expired_pro():
    User.objects(category='pro', expired_at=datetime.now(datetime.timezone.utc)).update(expired_at=None, category='free')
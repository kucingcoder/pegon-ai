from datetime import datetime, timezone
from models.user import User

def expired_pro():
    User.objects(
        category='pro',
        expired_at=datetime.now(timezone.utc)
    ).update(
        category='free',
        expired_at=None
    )
    print('clear expired pro users')
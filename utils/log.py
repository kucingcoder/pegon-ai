from models.log_activity import LogActivity

def log(user_id, activity, device):
    log = LogActivity(user_id=user_id, activity=activity, device=device)
    log.save()
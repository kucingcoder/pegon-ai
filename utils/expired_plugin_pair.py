import datetime
from models.plugins_pair import PluginsPair

def expired_plugin_pair():
    now = datetime.datetime.now()
    PluginsPair.objects(
        expired_at__lt=now,
        user_id=None
    ).delete()
    print('clear expired plugin pairs')
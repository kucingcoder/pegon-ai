import hashlib
import os
from dotenv import load_dotenv
from urllib.parse import quote
from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from mongoengine import connect
from controllers import user_bp, otp_bp, tutorial_bp, transliterate_bp, visualization_bp, payment_bp, admin_bp
from models.admin import Admin
from models.statistik_satuan_pendidikan import StatistikSatuanPendidikan
from utils import update_big_data
from apscheduler.schedulers.background import BackgroundScheduler

folders = [
    "storage",
    "storage/images",
    "storage/images/thumbnails",
    "storage/images/histories",
    "storage/models",
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

load_dotenv()

APP_KEY = os.environ.get('APP_KEY')

MONGODB_HOST = os.environ.get('MONGODB_HOST')
MONGODB_PORT = os.environ.get('MONGODB_PORT')
MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME')    
MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD')
MONGODB_AUTHDB = os.environ.get('MONGODB_AUTHDB')
MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE')

try:
    if not MONGODB_USERNAME or not MONGODB_PASSWORD or not MONGODB_AUTHDB:
        connection_string = f'mongodb://{MONGODB_HOST}:{MONGODB_PORT}/'
    else:
        connection_string = f'mongodb://{MONGODB_USERNAME}:{quote(MONGODB_PASSWORD)}@{MONGODB_HOST}:{MONGODB_PORT}/?directConnection=true&authSource={MONGODB_AUTHDB}'
    
    connect(db=MONGODB_DATABASE, host=connection_string)

    admin = Admin.objects().count()

    if admin == 0:
        admin = Admin(username='felix', password=hashlib.md5('c890Ir-$cMe7K9EC]WI_,+qDcG1&@XN.J+0LJutK2ROv&!8Gq}'.encode()).hexdigest())
        admin.save()
except Exception as e:
    exit(e)

app = Flask(__name__)
CORS(app)
app.secret_key = APP_KEY
app.config['JWT_SECRET_KEY'] = APP_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

jwt = JWTManager(app)

app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(otp_bp, url_prefix='/api/otp')
app.register_blueprint(tutorial_bp, url_prefix='/api/tutorial')
app.register_blueprint(transliterate_bp, url_prefix='/api/transliterate')
app.register_blueprint(visualization_bp, url_prefix='/api/visualization')
app.register_blueprint(payment_bp, url_prefix='/api/payment')
app.register_blueprint(admin_bp, url_prefix='/')

@app.route("/statistic")
def statistic():
    data = StatistikSatuanPendidikan.objects.first()

    fields = [
        "KB", "TK", "TPA", "SPS", "SD", "SMP",
        "SMA", "SMK", "SLB", "DIKMAS"
    ]
    values = [
        data.kbSederajat, data.tkSederajat, data.tpa, data.sps,
        data.sdSederajat, data.smpSederajat, data.smaSederajat,
        data.smkSederajat, data.slb, data.dikmas
    ]

    return render_template(
        "statistic.html",
        data=data,
        fields=fields,
        values=values
    )


@app.route('/')
def index():
    return {'message': 'API berjalan dengan baik!'}

update_big_data()

scheduler = BackgroundScheduler()
scheduler.add_job(update_big_data, 'cron', hour=0, minute=0)
scheduler.start()

if __name__ == '__main__':
    app.run()
from flask import Flask
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_seeder import FlaskSeeder
from sqlalchemy_utils import create_database, database_exists
import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

username = os.getenv("username")
password = os.getenv("password")
email = os.getenv("email")

DB_URL = f'postgresql://{username}:{password}@localhost/flasknotes'
app = Flask(__name__)

app.config['SECRET_KEY'] = '84025a69a81786a5da5ab95f190e1ca7b9f3570c83'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    # gmail authentication
    MAIL_USERNAME=email,
    MAIL_PASSWORD='aeaptxavqjgyyhng'
)
mail = Mail(app)

app.config['ELASTICSEARCH_URL'] = os.getenv("ELASTICSEARCH_URL")
app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

if not database_exists(DB_URL):
    print('Creating Database')
    create_database(DB_URL)

seeder = FlaskSeeder(app, db)

from notes import routes

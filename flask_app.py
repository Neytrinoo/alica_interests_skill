from flask import Flask
import logging
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    app.run()

from models import *
from routes import *

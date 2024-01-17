import os
from sqlalchemy import create_engine

BASEDIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_PATH = os.path.join(BASEDIR, 'static/assets/blog')
SECRET_KEY = "sdkfjlasdf%$^%^&qjluio23asdfu42903"
db_path = os.path.join(os.path.dirname(__file__), 'personal.sqlite')
engine = create_engine('sqlite:///{}'.format(db_path))
SQLALCHEMY_DATABASE_URI = str(engine.url)
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_ECHO = False

PER_PAGE = 10
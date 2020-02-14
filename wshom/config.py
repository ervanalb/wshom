import os
import pkg_resources
default_db_uri = "sqlite:///" + pkg_resources.resource_filename("wshom", "wshom.db")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "wshom-secret"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI") or default_db_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False

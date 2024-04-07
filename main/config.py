import os

class Config:
    SECRET_KEY = 'hello'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/images'
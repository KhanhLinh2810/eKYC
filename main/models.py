from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired

from main import db

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100), nullable=False)
    email = db.Column("email", db.String(100), nullable=False, unique=True)
    phone = db.Column("phone", db.String(12), nullable=False, unique=True)
    password = db.Column("password", db.String(20), nullable=False)
    portrait_path = db.Column("portrait_path", db.String(100), default="")

    def __init__(self, name, email, phone, password):
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload Image")

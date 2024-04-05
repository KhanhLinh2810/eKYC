from flask import Flask, redirect, url_for, render_template, request, session, flash, Response 
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename
import os
import cv2
import insightface
import numpy as np
from detection import detection 
# from recognition import recognition

app = Flask(__name__)
app.register_blueprint(detection, url_prefix="/")
# app.register_blueprint(recognition, url_prefix="/")

app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'
app.permanent_session_lifetime = timedelta(minutes=30)

model = insightface.app.FaceAnalysis(name='buffalo_l', providers='CPU')
model.prepare(ctx_id=0)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100))
    phone = db.Column("phone", db.String(12))
    password = db.Column("password", db.String(20))
    portrait_path = db.Column("portrait_path", db.String(100))

    def __init__(self, name, email, phone, password):
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password
        self.portrait_path = ""

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload Image")

@app.route("/")
def home():
    if "user_id" in session:
        return render_template("home.html")
    else:
        return redirect(url_for("login"))

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["numberPhone"]
        password = request.form["password"]
        
        
        user = users.query.filter_by(email=email).first()
        if user:
            flash("User already exist!")
            return redirect(url_for("register"))
        
        new_user = users(name=name, email=email, phone=phone, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for("uploadPortrait"))
    else:
        return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if(request.method == "POST"):
        email = request.form["email"]

        user = users.query.filter_by(email=email).first()
        if user: 
            session.permanent = True
            session["user_id"] = user._id
            if user.portrait_path == "":
                return redirect(url_for("uploadPortrait"))
            else:
                return redirect(url_for("user"))
        else:
            flash("User doesn't exist!")
            return redirect(url_for("login"))
    else:
        if "user_id" in session:
            return redirect(url_for("user"))

        return render_template("login.html")

@app.route("/portrait", methods=["POST", "GET"])
def uploadPortrait():
    form = UploadFileForm()
    if "user_id" in session:
        if(request.method == "POST"):
            if form.validate_on_submit():
                file = form.file.data
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    
                    user_id = session.get('user_id')
                    user = users.query.get(user_id)
                    user.portrait_path = file_path
                    db.session.commit()

                    flash("Portrait uploaded successfully")
                    return redirect(url_for("detectDeepfake"))
                else:
                    flash("Invalid file type. Only JPG, JPEG, PNG are allowed.")
                    return redirect(url_for("uploadPortrait"))
        else:
            return render_template("uploadPortrait.html", form=form)
    else:
        return redirect(url_for("login"))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @app.route("/video")
# def video():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# def generate_frames():
#     camera=cv2.VideoCapture(0)

#     if not (camera.isOpened()):
#         print("Could not open video device")

#     while True:
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
#             ret, buffer = cv2.imencode('.jpg', frame)
#             if not ret:
#                 break

#             frame = buffer.tobytes()
#         yield (b'--frame\r\n'
#                     b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/user")
def user():
    if "user_id" in session:
        user_id = session["user_id"]        
        user = users.query.get(user_id)
        return render_template("view.html", user=user)
    else:
        return redirect(url_for("login"))

@app.route("/view")
def view():
    return render_template("view.html", values=users.query.all())

@app.route("/recognition", methods=["POST", "GET"])
def recognize():
    if "user_id" in session:
        if request.method == "POST":
            file = request.files['image']
            if file and allowed_file(file.filename):
                unknow_img = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_COLOR)

                user_id = session.get('user_id')
                user = users.query.get(user_id)
                user_portrait = cv2.imread(user.portrait_path)

                faces1 = model.get(unknow_img)
                faces2 = model.get(user_portrait)

                face1 = faces1[0]
                face2 = faces2[0]

                threshold = 1

                distance = np.sum(np.square(face1.normed_embedding - face2.normed_embedding))
                if distance < threshold:
                    flash("Hai khuôn mặt giống nhau.")
                else:
                    flash("Hai khuôn mặt khác nhau.")

                return redirect(url_for("home"))
            else:
                flash("Invalid file type. Only JPG, JPEG, PNG are allowed.")
                return render_template("recognition.html")
        else:
            return render_template("recognition.html")
    else:
        return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
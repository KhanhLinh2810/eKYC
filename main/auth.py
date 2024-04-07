from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from datetime import timedelta
from werkzeug.utils import secure_filename
import os

from .models import users, UploadFileForm
from main import db

auth = Blueprint('auth', __name__, static_folder="../static", template_folder="../templates")
auth.permanent_session_lifetime = timedelta(minutes=30)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@auth.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["numberPhone"]
        password = request.form["password"]
        
        user = users.query.filter_by(email=email).first()
        if user:
            flash("User already exist!")
            return redirect(url_for("auth.register"))
        
        new_user = users(name=name, email=email, phone=phone, password=password)
        db.session.add(new_user)
        db.session.commit()

        session.permanent = True
        session["user_id"] = new_user._id
        
        return redirect(url_for("auth.uploadPortrait"))
    else:
        return render_template("register.html")

@auth.route("/login", methods=["POST", "GET"])
def login():
    if(request.method == "POST"):
        email = request.form["email"]

        user = users.query.filter_by(email=email).first()
        if user: 
            session.permanent = True
            session["user_id"] = user._id
            if user.portrait_path == "":
                return redirect(url_for("auth.uploadPortrait"))
            else:
                return redirect(url_for("user"))
        else:
            flash("User doesn't exist!")
            return redirect(url_for("auth.login"))
    else:
        if "user_id" in session:
            return redirect(url_for("user"))

        return render_template("login.html")


@auth.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("auth.login"))

@auth.route("/portrait", methods=["POST", "GET"])
def uploadPortrait():
    form = UploadFileForm()
    if "user_id" in session:
        user_id = session.get('user_id')
        user = users.query.get(user_id)
        
        if user.portrait_path != "":
            flash("You don't have permit to change your portrait!")
            return redirect(url_for("detection.detectDeepfake"))

        if(request.method == "POST"):
            if form.validate_on_submit():
                file = form.file.data
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join('static/images', filename)
                    file.save(file_path)
                    
                    user.portrait_path = file_path
                    db.session.commit()

                    flash("Portrait uploaded successfully")
                    return redirect(url_for("detection.detectDeepfake"))
                else:
                    flash("Invalid file type. Only JPG, JPEG, PNG are allowed.")
                    return redirect(url_for("auth.uploadPortrait"))
        else:
            return render_template("uploadPortrait.html", form=form)
    else:
        return redirect(url_for("auth.login"))


from flask import Blueprint, redirect, url_for, render_template, session

from .models import users

main = Blueprint("main", __name__, static_folder="../static", template_folder="../templates")

@main.route("/")
def home():
    if "user_id" in session:
        return render_template("home.html")
    else:
        return redirect(url_for("auth.login"))

@main.route("/user")
def user():
    if "user_id" in session:
        user_id = session["user_id"]        
        user = users.query.get(user_id)
        return render_template("profile.html", user=user)
    else:
        return redirect(url_for("auth.login"))
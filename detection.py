from flask import Blueprint, redirect, url_for, render_template, flash, session, request
from keras.models import load_model
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
import cv2
import numpy as np

detection = Blueprint("detection", __name__, static_folder="static", template_folder="templates")

model_detect_deepfake = load_model('Model.h5')

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@detection.route("/deepfake", methods=["POST", "GET"])
def detectDeepfake():
    if "user_id" in session:
        if request.method == "POST":
            file = request.files['image']
            if file and allowed_file(file.filename):
                img = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_COLOR)
                img = cv2.resize(img, (224, 224))
                img_array = image.img_to_array(img)
                img_array = np.expand_dims(img_array, axis=0)
                img_array = preprocess_input(img_array)

                predictions = model_detect_deepfake.predict(img_array)
                label = np.argmax(predictions)

                if label:
                    flash("It is a deepfake image")
                else:
                    flash("It is not a deepfake image")

                return redirect(url_for("home"))
            else:
                flash("Invalid file type. Only JPG, JPEG, PNG are allowed.")
                return render_template("detect.html")
        else:
            return render_template("detect.html")
    else:
        return redirect(url_for("login"))


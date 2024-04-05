# from flask import Blueprint, redirect, url_for, render_template, flash, session, request
# import insightface
# import cv2
# import numpy as np
# from run import users

# recognition = Blueprint("recognition", __name__, static_folder="static", template_folder="templates")

# model = insightface.app.FaceAnalysis(name='buffalo_l', providers='CPU')
# model.prepare(ctx_id=0)

# ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @recognition.route("/recognition", methods=["POST", "GET"])
# def recognize():
#     if "user_id" in session:
#         if request.method == "POST":
#             file = request.files['image']
#             if file and allowed_file(file.filename):
#                 unknow_img = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_COLOR)

#                 user_id = session.get('user_id')
#                 user = users.query.get(user_id)
#                 user_portrait = cv2.imread(user.portrait_path)

#                 faces1 = model.get(unknow_img)
#                 faces2 = model.get(user_portrait)

#                 face1 = faces1[0]
#                 face2 = faces2[0]

#                 threshold = 1

#                 distance = np.sum(np.square(face1.normed_embedding - face2.normed_embedding))
#                 if distance < threshold:
#                     flash("Hai khuôn mặt giống nhau.")
#                 else:
#                     flash("Hai khuôn mặt khác nhau.")

#                 return redirect(url_for("home"))
#             else:
#                 flash("Invalid file type. Only JPG, JPEG, PNG are allowed.")
#                 return render_template("recognition.html")
#         else:
#             return render_template("recognition.html")
#     else:
#         return redirect(url_for("login"))
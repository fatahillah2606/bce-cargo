from flask import Blueprint, jsonify, request, render_template
from connection import db_bce
from bson.objectid import ObjectId
from datetime import datetime
import bcrypt

# Collection
collection = db_bce.use_db()
userData = collection["users"]

# API
# Convert _id
def convert_mongo_data(data):
    return [{**item, "_id": str(item["_id"])} for item in data]

# Respon API
def respon_api(status, code, message, data):
    respon = {
        "status": status,
        "code": code,
        "message": message,
        "data": data if data else []
    }
    return jsonify(respon)

# Check duplicate entries
def checkEntries(kunci, isi):
    data = userData.find_one({kunci: isi})
    if data:
        return True
    else:
        return False

# Atur route
admin_route = Blueprint("admin", __name__)

# Route
@admin_route.route("/", methods=["GET", "POST"])
def login():
    return render_template("admin/auth/login.html")

@admin_route.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    return render_template("admin/pages/dashboard.html")

# Sistem autentikasi
@admin_route.route("/api/auth", methods=["GET", "POST"])
def autentikasi():
    try:
        # Register Admin (eksperimen)
        if request.method == "POST":
            if "sendUser" in request.form:
                name = str(request.form["name"])
                email = str(request.form["email"])
                password = request.form["password"]
                role = request.form["role"]

                # Cek entri duplikat
                emailExist = checkEntries("email", email)
                if emailExist:
                    return respon_api("error", 409, "Email sudah ada", [])
                
                # Enkripsi sandi
                pw = password.encode("utf-8")
                garam = bcrypt.gensalt()
                saltpass = bcrypt.hashpw(pw, garam)

                # Siapkan data

                DataUser = {
                    "_id": ObjectId(),
                    "name": name,
                    "email": email,
                    "password": saltpass,
                    "role": role,
                    "regist_date": datetime.now()
                }

                # Masukan data ke dalam database
                if userData.insert_one(DataUser):
                    return respon_api("success", 200, "Data sent", [])
                else:
                    return respon_api("error", 500, "Failed to sent", [])

            # Sistem login
            if "login" in request.form:
                email = str(request.form["email"])
                password = request.form["password"]

                # cek akun admin
                akun = userData.find_one({"email": email, "role": "admin"})
                if akun:
                    dbpw = akun["password"]
                    encodepw = password.encode("utf-8")

                    # validasi password
                    valid = bcrypt.checkpw(encodepw, dbpw)
                    if valid:
                        return respon_api("success", 200, "Verifikasi berhasil", [])
                    else:
                        return respon_api("error", 401, "Verifikasi gagal", [])
                else:
                    return respon_api("error", 401, "Verifikasi gagal", [])

    except Exception as error:
        return respon_api("error", 500, str(error), [])
        

# Experiment
@admin_route.route("/register", methods=["GET", "POST"])
def register():
    return render_template("admin/auth/regist.html")
from flask import Blueprint, jsonify, request, render_template, session, redirect, url_for
from connection import db_bce
from functools import wraps
from datetime import datetime, timedelta, timezone
import bcrypt, math

# Collection
collection = db_bce.use_db()
userData = collection["users"]

# API
# Convert _id
def convert_objectid_to_str(doc):
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

# Respon API
def respon_api(status, code, message, data, pagination):
    respon = {
        "status": status,
        "code": code,
        "message": message,
        "data": data if data else [],
        "pagination": pagination if pagination else {}
    }
    return jsonify(respon)

# Untuk proteksi halaman customer
def khusus_customer(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'customer':
            return redirect(url_for("customer.login"))
        return f(*args, **kwargs)
    return decorated_function
# Atur route
customer_route = Blueprint("customer", __name__)

# Route
@customer_route.route("/", methods=["GET", "POST"])

# LOGIIN
@customer_route.route("/login", methods=["GET", "POST"])
def login():
    if 'user_id' in session or session.get('role') == 'customer':
        return redirect(url_for("home"))
    else: 
        return render_template("customer/login.html")

#FORGOT PASSWORD
@customer_route.route("/forgotpw", methods=["GET", "POST"])
def forgotpw():
    return render_template("customer/forgotpw.html")

# REGISTER
@customer_route.route("/register", methods=["GET", "POST"])
def register():
    if 'user_id' in session or session.get('role') == 'customer':
        return redirect(url_for("home"))
    else: 
        return render_template("customer/register.html")


# ONGKIR
@customer_route.route("/ongkir", methods=["GET", "POST"])
@khusus_customer
def ongkir():
    return render_template("customer/ongkir.html")

# PESANAN
@customer_route.route("/pesanan", methods=["GET", "POST"])
@khusus_customer
def pesanan():
    return render_template("customer/pesanan.html")

#PROFILE
@customer_route.route("/profile", methods=["GET", "POST"])
@khusus_customer
def profile():
    return render_template("customer/profile.html")

# RIWAYAT PESANAN
@customer_route.route("/riwayat", methods=["GET", "POST"])
@khusus_customer
def riwayat():
    return render_template("customer/riwayat.html")

# Eksperimen
@customer_route.route("/tes", methods=["GET", "POST"])
@khusus_customer
def tes():
    return render_template("customer/tes.html")

# Logout
@customer_route.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("customer.login"))

#API Route
#Sistem Autentikasi
@customer_route.route("/api/auth", methods=["GET", "POST"])
def authetikasi():
    try:
        #Sistem Login
        if "login" in request.form:
            email = str(request.form["email"])
            password = request.form["password"]

            # Cek akun customer
            akun = userData.find_one({"email": email, "role": "customer"})
            if akun:
                dbpw = akun["password"]
                dbpw = dbpw.encode("utf-8")
                encodepw = password.encode("utf-8")

                # Validasi Password
                valid = bcrypt.checkpw(encodepw, dbpw)
                if valid:

                    # Buat sesi
                    session.permanent = True
                    session['kedaluwarsa'] = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
                    session["user_id"] = str(akun["_id"])
                    session["name"] = akun["name"]
                    session["email"] = akun["email"]
                    session["role"] = akun["role"]

                    return respon_api("success", 200, "Verifikasi berhasil", [], {})
                else:
                    return respon_api("error", 401, "Sandi salah", [], {})
            else:
                return respon_api("error", 401, "Akun tidak tersedia", [], {})
    
    except Exception as error:
        return respon_api("error", 500, str(error), [], {})
    
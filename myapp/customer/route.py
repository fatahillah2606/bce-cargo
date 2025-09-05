from flask import Blueprint, jsonify, request,render_template, session, redirect, url_for, current_app
from connection import db_bce
from functools import wraps
from datetime import datetime, timedelta, timezone
import bcrypt, math, requests
from myapp.customer.generate_code import generate_verification_code
from bson.objectid import ObjectId
from myapp.email_utils import send_email_smtp

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

# Tampilkan Semua Data
def tampilkanDataSpesifik(koleksi, oid):
    data = koleksi.find_one({"_id": ObjectId(oid)})
    if data:
        return respon_api("success", 200, str("Data tersedia"), convert_objectid_to_str(data), {})
    else:
        return respon_api("error", 404, str("Data tidak tersedia"), [], {}), 404

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

# REGISTER
@customer_route.route("/register", methods=["GET", "POST"])
def register():
    if 'user_id' in session or session.get('role') == 'customer':
        return redirect(url_for("home"))
    else: 
        return render_template("customer/auth/register.html")

# LOGIIN
@customer_route.route("/login", methods=["GET", "POST"])
def login():
    if 'user_id' in session or session.get('role') == 'customer':
        return redirect(url_for("home"))
    else: 
        return render_template("customer/auth/login.html") 

#FORGOT PASSWORD
@customer_route.route("/forgotpw", methods=["GET", "POST"])
def forgotpw():
    return render_template("customer/auth/forgotpw.html")

# VERIFIKASI
@customer_route.route("/verif", methods=["GET", "POST"])
def verif():
    return render_template("customer/auth/verif.html")

# ONGKIR
@customer_route.route("/ongkir", methods=["GET", "POST"])
@khusus_customer
def ongkir():
    return render_template("customer/pages/ongkir.html")

# PESANAN
@customer_route.route("/pesanan", methods=["GET", "POST"])
@khusus_customer
def pesanan():
    return render_template("customer/pages/pesanan.html")

#PROFILE
@customer_route.route("/profile", methods=["GET", "POST"])
@khusus_customer
def profile():
    return render_template("customer/pages/profile.html")

# RIWAYAT PESANAN
@customer_route.route("/riwayat", methods=["GET", "POST"])
@khusus_customer
def riwayat():
    return render_template("customer/pages/riwayat.html")

# Eksperimen
@customer_route.route("/tes", methods=["GET", "POST"])
@khusus_customer
def tes():
    return render_template("customer/pages/tes.html")

# Logout
@customer_route.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

#API Route
# Data Pengguna
@customer_route.route("/api/data/user", methods=["GET","POST"])
@khusus_customer
def dataPelanggan():
    uid = request.args.get("uid")
    return tampilkanDataSpesifik(userData, uid)



# Autentikasi
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

        # Sistem Registrasi
        if "register" in request.form:
            email = str(request.form["email"])
            password = request.form["confirm_password"]
            fullname = str(request.form["fullname"])

            # Cek akun customer
            akun = userData.find_one({"email": email, "role": "customer"})
            if akun: 
                return respon_api("error", 409, "Email Sudah Terdaftar", [], {})
            else:

                # Enkripsi sandi
                hashedPass = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

                # decode ke string
                hashedPass = hashedPass.decode("utf-8")

                # Object ID untuk User
                iduser = ObjectId()

                kode = generate_verification_code()

                # Enkripsi kv
                hashedKode = bcrypt.hashpw(kode.encode("utf-8"), bcrypt.gensalt())

                # decode ke string
                hashedKode = hashedKode.decode("utf-8")
                expired_at = (datetime.now(timezone.utc) + timedelta(minutes=5))

                # Kirim Kode Verifikasi Ke Database
                SimpanKode = {
                    "kode": hashedKode, 
                    "is_verified": False,
                    "expired_at": expired_at
                }

                # Siapkan data
                DataUser = {
                    "_id": iduser,
                    "name": fullname,
                    "email": email,
                    "password": hashedPass,
                    "role": "customer",
                    "kode_verif": SimpanKode,
                    "regist_date": datetime.now(),
                    "is_active": False
                }
                
                # Masukan data ke dalam database
                if userData.insert_one(DataUser):
                    print("Akun berhasil dibuat")

                    # Buat sesi
                    session.permanent = True
                    session['kedaluwarsa'] = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
                    session["user_id"] = str(iduser)
                    session["name"] = fullname
                    session["email"] = email
                    session["role"] = "customer"

                    # Kirim Email Ke Pelanggan
                    recipient = email

                    # Data dinamis untuk template
                    context = {
                        'USER_NAME': fullname,
                        'APP_NAME': "CV. Bahtera Cahaya Express",
                        'CODE': kode,
                        'EXP_MINUTES': 5,
                        'SUPPORT_EMAIL': "atepbcecargo@gmail.com",
                        'YEAR': datetime.now().year
                    }

                    # Render template Jinja (HTML & plain-text)
                    html_body = render_template('emails/verif.html', **context)
                    text_body = render_template('emails/verif.txt', **context)

                    send_email_smtp(
                        host=current_app.config['MAIL_SERVER'],
                        port=current_app.config['MAIL_PORT'],
                        sender=current_app.config['MAIL_SENDER'],
                        to=recipient,
                        subject=f"Kode verifikasi akun anda adalah " + kode,
                        html_body=html_body,
                        text_body=text_body
                    )

                    print("Email berhasil dikirim")
                    
                    return respon_api("success", 200, "Registrasi Berhasil", [], {})
                else:
                    return respon_api("error", 500, "Registrasi Gagal", [], {}), 500

    except Exception as error:
        return respon_api("error", 500, str(error), [], {})
    
# Verifikasi
@customer_route.route("/api/data/verifikasi", methods=["GET", "POST"])
def verifikasi():
    try:
        
        kode = request.form["kode"]
        # Cek akun customer
        akun = userData.find_one({"_id": ObjectId(session["user_id"])})
        if akun:
            kv = akun["kode_verif"]
            dbkv = kv["kode"]
            dbkv = dbkv.encode("utf-8")
            encodekv = kode.encode("utf-8")

            # Validasi Password
            valid = bcrypt.checkpw(encodekv, dbkv)
            if valid:
                userData.update_one({"_id": ObjectId(session["user_id"])}, {"$set": {"kode_verif.is_verified": True, "is_active": True}})
                return respon_api("success", 200, "Verifikasi berhasil", [], {})
            else:
                return respon_api("error", 401, "Kode Salah", [], {})
        else:
            return respon_api("error", 401, "Akun tidak tersedia", [], {})
        # return respon_api("success", 200, "Fetch berhasil", str(request.form), {})
    
    except Exception as error:
        return respon_api("error", 500, str(error), [], {})
    


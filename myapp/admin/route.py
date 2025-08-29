from flask import Blueprint, jsonify, request, render_template, session, flash, redirect, url_for
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired
from functools import wraps
from connection import db_bce
from bson.objectid import ObjectId
from datetime import datetime, timedelta, timezone
import bcrypt, math

# Collection
collection = db_bce.use_db()
userData = collection["users"]

# API
# Convert _id
def convert_objectid_to_str(doc):
    if isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, dict):
        return {k: convert_objectid_to_str(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [convert_objectid_to_str(i) for i in doc]
    else:
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
def tampilkanSemuaData(koleksi, page, limit, query):
    halaman = int(page if page else 1)
    batas = int(limit if limit else 10)
    lewati = (halaman - 1) * batas

    total_items = koleksi.count_documents({})
    total_halaman = math.ceil(total_items / batas)

    cursor = koleksi.find(query).sort("_id", -1).skip(lewati).limit(batas)
    data = [convert_objectid_to_str(doc) for doc in cursor]

    if data:
        pageTest = {
            "current_page": halaman,
            "per_page": batas,
            "total_items": total_items,
            "total_pages": total_halaman
        }

        return respon_api("success", 200, str("Data tersedia"), data, pageTest)
    else:
        return respon_api("error", 404, str("Data tidak tersedia"), [], {}), 404

# Tampilkan data spesifik
def tampilkanDataSpesifik(koleksi, oid):
    data = koleksi.find_one({"_id": ObjectId(oid)})
    if data:
        return respon_api("success", 200, str("Data tersedia"), convert_objectid_to_str(data), {})
    else:
        return respon_api("error", 404, str("Data tidak tersedia"), [], {}), 404


# Check duplicate entries
def checkEntries(kunci, isi):
    data = userData.find_one({kunci: isi})
    if data:
        return True
    else:
        return False

# Untuk proteksi halaman admin
def khusus_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "admin":
            if request.path.startswith("/admin/api/"):
                return respon_api("error", 403, str("Anda tidak memiliki akses"), [], {}), 403
            else:
                return redirect(url_for("admin.login"))

        return f(*args, **kwargs)
    return decorated_function

# Atur route
admin_route = Blueprint("admin", __name__)

@admin_route.context_processor
def inject_globals():
    return dict(
        nama_pengguna=session.get("name"),
        email_pengguna=session.get("email"),
        role_pengguna=session.get("role"),
        active_page=None  # ini bisa dioverride di masing-masing route
    )


# Route
@admin_route.route("/")
def login():
    if "user_id" in session or session.get("role") == "admin":
        return redirect(url_for("admin.dashboard"))
    else:
        return render_template("admin/auth/login.html")

# Halaman
@admin_route.route("/dashboard")
@khusus_admin
def dashboard():
    return render_template("admin/pages/dashboard.html", active_page="dashboard")

@admin_route.route("/pesanan_masuk")
@khusus_admin
def pesanan_masuk():
    return render_template("admin/pages/pesanan_masuk.html", active_page="pesanan_masuk")

@admin_route.route("/invoice")
@khusus_admin
def invoice():
    return render_template("admin/pages/invoice.html", active_page="invoice")

@admin_route.route("/laporan")
@khusus_admin
def laporan():
    return render_template("admin/pages/laporan.html", active_page="laporan")

@admin_route.route("/manajemen_pengguna")
@khusus_admin
def manajemen_pengguna():
    return render_template("admin/pages/manajemen_pengguna.html", active_page="manajemen_pengguna")

@admin_route.route("/riwayat_pesanan")
@khusus_admin
def riwayat_pesanan():
    return render_template("admin/pages/riwayat_pesanan.html", active_page="pesanan_masuk")

@admin_route.route("/status")
@khusus_admin
def status():
    return render_template("admin/pages/status.html", active_page="pesanan_masuk")

@admin_route.route("/kategori")
@khusus_admin
def kategori():
    return render_template("admin/pages/kategori.html", active_page="kategori")

@admin_route.route("/tarif")
@khusus_admin
def tarif():
    return render_template("admin/pages/tarif.html", active_page="tarif")

@admin_route.route("/keluhan")
@khusus_admin
def keluhan():
    return render_template("admin/pages/keluhan.html", active_page="keluhan")

# Logout
@admin_route.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin.login"))

# API Route
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
                    return respon_api("error", 409, "Email sudah ada", [], {}), 409
                
                # Enkripsi sandi
                hashedPass = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

                # decode ke string
                hashedPass = hashedPass.decode("utf-8")

                # Siapkan data
                DataUser = {
                    "_id": ObjectId(),
                    "name": name,
                    "email": email,
                    "password": hashedPass,
                    "role": role,
                    "regist_date": datetime.now()
                }

                # Masukan data ke dalam database
                if userData.insert_one(DataUser):
                    return respon_api("success", 200, "Data sent", [], {})
                else:
                    return respon_api("error", 500, "Failed to sent", [], {}), 500

            # Sistem login
            if "login" in request.form:
                email = str(request.form["email"])
                password = request.form["password"]

                # cek akun admin
                akun = userData.find_one({"email": email, "role": "admin"})
                if akun:
                    dbpw = akun["password"]
                    dbpw = dbpw.encode("utf-8")
                    encodepw = password.encode("utf-8")

                    # validasi password
                    valid = bcrypt.checkpw(encodepw, dbpw)
                    if valid:

                        # Buat sesi
                        session.permanent = True
                        session["kedaluwarsa"] = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
                        session["user_id"] = str(akun["_id"])
                        session["name"] = akun["name"]
                        session["email"] = akun["email"]
                        session["role"] = akun["role"]

                        return respon_api("success", 200, "Verifikasi berhasil", [], {})
                    else:
                        return respon_api("error", 401, "Email atau Sandi salah", [], {}), 401
                else:
                    return respon_api("error", 401, "Email atau Sandi salah", [], {}), 401

    except Exception as error:
        return respon_api("error", 500, str(error), [], {})

# Pemesanan Kargo
@admin_route.route("/api/data/pesanan", methods=["GET", "POST"])
@khusus_admin
def dataPesanan():
    try:
        if request.method == "GET":
            statusPesanan = request.args.getlist("status")
            excludeStatus = request.args.getlist("exclude_status")
            
            if statusPesanan:
                # Ambil query apa saja yang di filter berdasarkan status
                queryPencarian = {"$or": [{"status": status} for status in statusPesanan]}

                # Cari berdasarkan status lalu tampilkan
                pemesanan = collection["pemesanan_kargo"]
                return tampilkanSemuaData(pemesanan, request.args.get("page", 1), request.args.get("limit", 10), queryPencarian)
            
            elif excludeStatus:
                # Ambil query apa saja yang di kecualikan berdasarkan status
                queryPencarian = {"status": {"$nin": [pengecualian for pengecualian in excludeStatus]}}

                # Tampilkan data dengan pengecualian status
                pemesanan = collection["pemesanan_kargo"]
                return tampilkanSemuaData(pemesanan, request.args.get("page", 1), request.args.get("limit", 10), queryPencarian)

            else:
                # Tampilkan semua data tanpa filtrasi
                pemesanan = collection["pemesanan_kargo"]
                return tampilkanSemuaData(pemesanan, request.args.get("page", 1), request.args.get("limit", 10), {})

    except Exception as error:
        return respon_api("error", 500, str(error), [], {}), 500
    
# Tarif
@admin_route.route("/api/data/tarif", methods=["GET", "POST", "DELETE"])
@khusus_admin
def dataTarif():
    try:
        tarif = collection["tarif"]

        # Method POST
        if request.method == "POST":

            # Tambah tarif
            if "tambahTarif" in request.form:
                rute = str(request.form["rute"])
                destinasi = str(request.form["destinasi"])
                origin = str(request.form["origin"])
                jenis = str(request.form["jenis"])
                moda = str(request.form["moda"])
                harga = int(request.form["harga"])

                DataTarif = {
                    "_id": ObjectId(),
                    "rute": rute,
                    "destinasi": destinasi,
                    "origin": origin,
                    "jenis": jenis,
                    "moda": moda,
                    "harga": harga
                }

                if tarif.insert_one(DataTarif):
                    return respon_api("success", 200, "Tarif baru berhasil ditambahkan", [], {})
                else:
                    return respon_api("error", 500, "Gagal menambahkan data tarif", [], {}), 500

            # Edit tarif
            if "editTarif" in request.form:
                objekId = str(request.form["objekId"])
                rute = str(request.form["rute"])
                destinasi = str(request.form["destinasi"])
                origin = str(request.form["origin"])
                jenis = str(request.form["jenis"])
                moda = str(request.form["moda"])
                harga = int(request.form["harga"])

                DataTarif = {
                    "rute": rute,
                    "destinasi": destinasi,
                    "origin": origin,
                    "jenis": jenis,
                    "moda": moda,
                    "harga": harga
                }

                if tarif.update_one({"_id": ObjectId(objekId)}, {"$set": DataTarif}):
                    return respon_api("success", 200, "Tarif berhasil diubah", [], {})
                else:
                    return respon_api("error", 500, "Gagal mengubah data tarif", [], {}), 500

            else:
                return respon_api("error", 400, "Bad request", [], {}), 400
        
        # Method DELETE
        elif request.method == "DELETE":
            data_json = request.get_json()

            if tarif.delete_one({"_id": ObjectId(data_json.get("ObjekId"))}):
                return respon_api("success", 200, "Tarif berhasil dihapus", [], {})
            else:
                return respon_api("error", 500, "Gagal menghapus data tarif", [], {}), 500

        # Method GET (default)
        else:
            oid = request.args.get("oid")
            if oid:
                return tampilkanDataSpesifik(tarif, oid)
            else:
                return tampilkanSemuaData(tarif, request.args.get("page", 1), request.args.get("limit", 10), {})

    except Exception as error:
        return respon_api("error", 500, str(error), [], {}), 500

# Kategori Barang Kargo
@admin_route.route("/api/data/kategori", methods=["GET", "POST"])
@khusus_admin
def dataKategori():
    try:
        if request.method == "GET":
            kategori_barang = collection["kategori_barang_kargo"]
            return tampilkanSemuaData(kategori_barang, request.args.get("page", 1), request.args.get("limit", 10), {})

    except Exception as error:
        return respon_api("error", 500, str(error), [], {})
    
# Keluhan pelanggan
@admin_route.route("/api/data/feedback", methods=["GET", "POST"])
@khusus_admin
def dataFeedback():
    try:
        if request.method == "GET":
            feedback = collection["feedback"]
            return tampilkanSemuaData(feedback, request.args.get("page", 1), request.args.get("limit", 10), {})

    except Exception as error:
        return respon_api("error", 500, str(error), [], {})

# Experiment
@admin_route.route("/register", methods=["GET", "POST"])
def register():
    return render_template("admin/auth/regist.html")
from flask import Blueprint, jsonify, request, render_template, session, flash, redirect, url_for, current_app, abort
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired
from datetime import datetime, timedelta, timezone
from pymongo import ReturnDocument
from functools import wraps
from markupsafe import escape
from connection import db_bce
from bson.objectid import ObjectId
from myapp.email_utils import send_email_smtp
import bcrypt, math, pytz

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
    elif isinstance(doc, str):  
        # sanitasi string dengan escape
        return escape(doc)
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
def tampilkanSemuaData(koleksi, page, limit, query, excluded):
    halaman = int(page if page else 1)
    batas = int(limit if limit else 10)
    lewati = (halaman - 1) * batas

    total_items = koleksi.count_documents(query)
    total_halaman = math.ceil(total_items / batas)

    cursor = koleksi.find(query, excluded).sort("_id", -1).skip(lewati).limit(batas)
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
        return respon_api("success", 200, str("Data tidak tersedia"), [], {})

# Tampilkan data spesifik
def tampilkanDataSpesifik(koleksi, oid):
    data = koleksi.find_one({"_id": ObjectId(oid)})
    if data:
        return respon_api("success", 200, str("Data tersedia"), convert_objectid_to_str(data), {})
    else:
        return respon_api("success", 200, str("Data tidak tersedia"), [], {})

# Etc
# Ubah UTC ke Indonesia
def convert_utc_to_indonesia(waktu):
    if waktu.tzinfo is None:
        zona_utc = pytz.utc
        waktu = zona_utc.localize(waktu)
    
    zona_wib = pytz.timezone("Asia/Jakarta")
    waktu = waktu.astimezone(zona_wib)
    
    return waktu.strftime("%d %B %Y, %H:%M:%S WIB")

# Format rupiah
def format_rupiah(angka):
    formatted = f"{angka:,.0f}"
    formatted = formatted.replace(',', '.')
    return f"Rp {formatted}"

# Buat kode invoice
def generate_kode_invoice() -> str:
    counters = collection["counters"]

    # format tanggal: yymmdd
    tanggal = datetime.now().strftime("%y%m%d")

    # key khusus untuk invoice + tanggal
    key = f"INV-{tanggal}"

    # update counter di MongoDB (atomic)
    doc = counters.find_one_and_update(
        {"_id": key},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )

    urutan = doc["sequence_value"]
    unique_id = f"{urutan:03}"  # selalu 3 digit

    return f"INV-{tanggal}-{unique_id}"

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
    return {
        "nama_pengguna": session.get("name"),
        "email_pengguna": session.get("email"),
        "role_pengguna": session.get("role"),
        "active_page": None,  # ini bisa dioverride di masing-masing route
        "current_time": datetime.now(timezone.utc)
    }

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

@admin_route.route("/detail_invoice/<kode_invoice>")
@khusus_admin
def detailInvoice(kode_invoice):
    detail_invoice = collection["invoice"].find_one({"kode_invoice": kode_invoice})

    if detail_invoice:
        detail_invoice["tanggal_invoice"] = convert_utc_to_indonesia(detail_invoice["tanggal_invoice"])

        detail_invoice["rincian_pembayaran"]["subtotal"] = format_rupiah(detail_invoice["rincian_pembayaran"]["subtotal"])
        detail_invoice["rincian_pembayaran"]["surcharge_dg"] = format_rupiah(detail_invoice["rincian_pembayaran"]["surcharge_dg"])
        detail_invoice["rincian_pembayaran"]["biaya_packing"] = format_rupiah(detail_invoice["rincian_pembayaran"]["biaya_packing"])
        detail_invoice["rincian_pembayaran"]["total"] = format_rupiah(detail_invoice["rincian_pembayaran"]["total"])
        
        return render_template("admin/pages/detail_invoice.html", active_page="invoice", detail_invoice = detail_invoice)
    else:
        abort(404)

@admin_route.route("/laporan")
@khusus_admin
def laporan():
    return render_template("admin/pages/laporan.html", active_page="laporan")

@admin_route.route("/manajemen_pengguna")
@khusus_admin
def manajemen_pengguna():
    return render_template("admin/pages/manajemen_pengguna.html", active_page="manajemen_pengguna")

@admin_route.route("/manajemen_customer")
@khusus_admin
def manajemen_customer():
    return render_template("admin/pages/manajemen_customer.html", active_page="manajemen_pengguna")

@admin_route.route("/riwayat_pesanan")
@khusus_admin
def riwayat_pesanan():
    return render_template("admin/pages/riwayat_pesanan.html", active_page="pesanan_masuk")

@admin_route.route("/status")
@khusus_admin
def status():
    print(session.get("kedaluwarsa"))
    return render_template("admin/pages/status.html", active_page="pesanan_masuk")

@admin_route.route("/detail_pesanan/<kode_pesanan>")
@khusus_admin
def detailPesanan(kode_pesanan):
    # Ambil data pemesanan
    detailPesanan = collection["pemesanan_kargo"].find_one({"kode_pemesanan": kode_pesanan})

    # Apakah pesanan ada?
    if detailPesanan:
        detailPesanan["tanggal_pemesanan"] = convert_utc_to_indonesia(detailPesanan["tanggal_pemesanan"])
        detailPesanan["harga_total"] = format_rupiah(detailPesanan["harga_total"])

        return render_template("admin/pages/detail_pesanan.html", active_page="pesanan_masuk", detail_pesanan = detailPesanan)
    else:
        abort(404)

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

# handler untuk error pages
@admin_route.app_errorhandler(403)
@khusus_admin
def forbidden_error(error):
    return render_template("admin/errors/403.html"), 403

@admin_route.app_errorhandler(404)
@khusus_admin
def not_found_error(error):
    return render_template("admin/errors/404.html"), 404

@admin_route.app_errorhandler(500)
@khusus_admin
def internal_error(error):
    return render_template("admin/errors/500.html"), 500

@admin_route.app_errorhandler(503)
@khusus_admin
def service_unavailable(error):
    return render_template("admin/errors/503.html"), 503

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
        pemesanan = collection["pemesanan_kargo"]

        if request.method == "POST":
            return respon_api("error", 500, "Request method POST belum dibuat", [], {}), 500
            
        else:
            statusPesanan = request.args.getlist("status")
            excludeStatus = request.args.getlist("exclude_status")
            idPemesanan = request.args.get("id")
            tahun = request.args.get("tahun")
            
            if statusPesanan:
                # Ambil query apa saja yang di filter berdasarkan status
                queryPencarian = {"$or": [{"status": status} for status in statusPesanan]}

                # Cari berdasarkan status lalu tampilkan
                return tampilkanSemuaData(pemesanan, request.args.get("page", 1), request.args.get("limit", 10), queryPencarian, {})
            
            elif excludeStatus:
                # Ambil query apa saja yang di kecualikan berdasarkan status
                queryPencarian = {"status": {"$nin": [pengecualian for pengecualian in excludeStatus]}}

                # Tampilkan data dengan pengecualian status
                return tampilkanSemuaData(pemesanan, request.args.get("page", 1), request.args.get("limit", 10), queryPencarian, {})
            
            elif idPemesanan:
                # Tampilkan satu baris data
                return tampilkanDataSpesifik(pemesanan, idPemesanan)
            
            elif tahun:
                # Filter berdasarkan tahun
                tahun = int(request.args.get("tahun"))
                queryPencarian = {
                    "tanggal_pemesanan": {
                        "$gte": datetime.fromisoformat(f"{str(tahun)}-01-01T00:00:00.000Z"),
                        "$lt": datetime.fromisoformat(f"{str(tahun + 1)}-01-01T00:00:00.000Z")
                    }
                }

                return tampilkanSemuaData(pemesanan, request.args.get("page", 1), request.args.get("limit", 10), queryPencarian, {})

            else:
                # Tampilkan semua data tanpa filtrasi
                return tampilkanSemuaData(pemesanan, request.args.get("page", 1), request.args.get("limit", 10), {}, {})

    except Exception as error:
        return respon_api("error", 500, str(error), [], {}), 500
    
# API Detail Pesanan
@admin_route.route("/api/data/detail_pesanan/<kode_pesanan>", methods=["GET", "POST"])
@khusus_admin
def APIdetailPesanan(kode_pesanan):
    try:
        # Ambil data pemesanan
        detailPesanan = collection["pemesanan_kargo"].find_one({"kode_pemesanan": kode_pesanan})
        dataPelanggan = collection["data_pelanggan"].find_one({"_id": detailPesanan["pelanggan_id"]})
        akunPelanggan = collection["users"].find_one({"_id": dataPelanggan["user_id"]})
        if request.method == "POST":
            # Tolak pesanan
            if "tolak_pesanan" in request.form:
                if collection["pemesanan_kargo"].update_one({"kode_pemesanan": kode_pesanan}, {"$set": {"status": "Ditolak"}}):
                    alasanPenolakan = str(request.form["alasan_penolakan"])

                    # Kirim email tanda pesanan ditolak
                    context = {
                        "tanggal_pemesanan": convert_utc_to_indonesia(detailPesanan["tanggal_pemesanan"]),
                        "nama_pengirim": dataPelanggan["nama_lengkap"],
                        "kode_pemesanan": detailPesanan["kode_pemesanan"],
                        "alasan_penolakan": alasanPenolakan,
                        "SUPPORT_URL": "https://wa.me/6281291244237",
                        "APP_NAME": "CV. Bahtera Cahaya Express"
                    }

                    # Render template Jinja (HTML & plain-text)
                    html_body = render_template("emails/customer/penolakan_pesanan.html", **context)
                    text_body = render_template("emails/customer/penolakan_pesanan.txt", **context)

                    send_email_smtp(
                        host = current_app.config["MAIL_SERVER"],
                        port = current_app.config["MAIL_PORT"],
                        sender = current_app.config["MAIL_SENDER"],
                        to = akunPelanggan["email"],
                        subject = f"Pesanan ditolak",
                        html_body = html_body,
                        text_body = text_body
                    )

                    return respon_api("success", 200, f"Pesanan {kode_pesanan} ditolak", [], {})
                else:
                    return respon_api("error", 500, f"Kesalahan dalam proses menolak pesanan", [], {}), 500
                
            elif "terima_pesanan" in request.form:
                subTotal = int(request.form.get("subtotal"))
                surCharge = int(request.form.get("surcharge", 0))
                packing = int(request.form.get("packing", 0))
                diskon = int(request.form.get("discount", 0))
                totalBiaya = int(request.form.get("totalAmount"))
                catatan = request.form.get("notes", "-")

                terimaPesanan = collection["pemesanan_kargo"].update_one({"kode_pemesanan": kode_pesanan}, {"$set": {"status": "Diproses", "harga_total": totalBiaya}})

                if terimaPesanan:
                    # Buat invoice
                    dataInvoice = {
                        "_id": ObjectId(),
                        "kode_invoice": generate_kode_invoice(),
                        "pemesanan_id": detailPesanan["_id"],
                        "pelanggan_id": dataPelanggan["_id"],
                        "tanggal_invoice": datetime.now(timezone.utc),
                        "metode_pembayaran": "Transfer Bank",
                        "status_pembayaran": "Belum Dibayar",
                        "rincian_pembayaran": {
                            "subtotal": subTotal,
                            "surcharge_dg": surCharge,
                            "biaya_packing": packing,
                            "diskon": diskon,
                            "total": totalBiaya
                        },
                        "catatan": catatan,
                        "updated_at": datetime.now(timezone.utc)
                    }

                    buatInvoice = collection["invoice"].insert_one(dataInvoice)
                    
                    if buatInvoice:
                        # List barang yang ada di detailPesanan
                        listDataBarang = []
                        for idbr in detailPesanan["barang_ids"]:
                            barang = collection["data_barang"].find_one({"_id": ObjectId(idbr)})
                            if barang:
                                kategori = collection["kategori_barang_kargo"].find_one({"_id": barang["kategori_id"]})
                                if kategori:
                                    barang["nama_kategori"] = kategori["nama_kategori"]  # tambahin nama kategori langsung
                                else:
                                    barang["nama_kategori"] = None  # fallback kalau kategori gak ketemu
                                listDataBarang.append(barang)
                        
                        context = {
                            "tanggal_pemesanan": convert_utc_to_indonesia(detailPesanan["tanggal_pemesanan"]),
                            "nama_pengirim": dataPelanggan["nama_lengkap"],
                            "kode_pemesanan": detailPesanan["kode_pemesanan"],
                            "invoice_number": dataInvoice["kode_invoice"],
                            "tanggal_invoice": convert_utc_to_indonesia(dataInvoice["tanggal_invoice"]),
                            "nama_pengirim": detailPesanan["nama_pengirim"],
                            "alamat_pengirim": detailPesanan["alamat_pengirim"],
                            "no_hp_pengirim": detailPesanan["no_hp_pengirim"],
                            "data_barang": listDataBarang,
                            "subtotal": format_rupiah(dataInvoice["rincian_pembayaran"]["subtotal"]),
                            "surcharge_dg": format_rupiah(dataInvoice["rincian_pembayaran"]["surcharge_dg"]),
                            "biaya_packing": format_rupiah(dataInvoice["rincian_pembayaran"]["biaya_packing"]),
                            "diskon": f"{dataInvoice["rincian_pembayaran"]["diskon"]}%",
                            "total": format_rupiah(dataInvoice["rincian_pembayaran"]["total"]),
                            "APP_NAME": "CV. Bahtera Cahaya Express"
                        }

                        # Render template Jinja (HTML & plain-text)
                        html_body = render_template("emails/customer/pesanan_diterima.html", **context)
                        text_body = render_template("emails/customer/pesanan_diterima.txt", **context)

                        send_email_smtp(
                            host = current_app.config["MAIL_SERVER"],
                            port = current_app.config["MAIL_PORT"],
                            sender = current_app.config["MAIL_SENDER"],
                            to = akunPelanggan["email"],
                            subject = f"Pesanan diterima",
                            html_body = html_body,
                            text_body = text_body
                        )

                        return respon_api("success", 200, f"Pesanan {kode_pesanan} diterima", [], {})
                        
                    else:
                        return respon_api("error", 500, f"Kesalahan dalam proses terima pesanan", [], {}), 500

                else:
                    return respon_api("error", 500, f"Kesalahan dalam proses terima pesanan", [], {}), 500

            elif "update_status" in request.form:
                status = str(request.form.get("status"))
                adminNotes = str(request.form.get("notes"))

                updateStatus = collection["pemesanan_kargo"].update_one({"kode_pemesanan": kode_pesanan}, {"$set": {"status": status}})

                if updateStatus:
                    context = {
                        "nama_pelanggan": detailPesanan["nama_pengirim"],
                        "kode_pemesanan": detailPesanan["kode_pemesanan"],
                        "status_pesanan": status,
                        "catatan_admin": adminNotes,
                        "YEAR": datetime.now(timezone.utc).year,
                        "APP_NAME": "CV. Bahtera Cahaya Express"
                    }

                    # Render template Jinja (HTML & plain-text)
                    html_body = render_template("emails/customer/update_status.html", **context)
                    text_body = render_template("emails/customer/update_status.txt", **context)

                    send_email_smtp(
                        host = current_app.config["MAIL_SERVER"],
                        port = current_app.config["MAIL_PORT"],
                        sender = current_app.config["MAIL_SENDER"],
                        to = akunPelanggan["email"],
                        subject = f"Pembaruan status pesanan",
                        html_body = html_body,
                        text_body = text_body
                    )

                    return respon_api("success", 200, "Status pesanan diperbarui", [], {})
                else:
                    return respon_api("error", 500, "Kesalahan memperbarui status", [], {}), 500

            else:
                return respon_api("error", 400, "Bad request", [], {}), 400
            
        else:
            listBarang = request.args.get("list_barang")
            if listBarang:
                # Ambil data barang
                barang_ids = [id_barang for id_barang in detailPesanan["barang_ids"]]
                return tampilkanSemuaData(collection["data_barang"], request.args.get("page", 1), request.args.get("limit", 10), {"_id": {"$in": barang_ids}}, {})
            
            else:
                return tampilkanDataSpesifik(collection["pemesanan_kargo"], detailPesanan["_id"])

    except Exception as error:
        print(error)
        return respon_api("error", 500, str(error), [], {}), 500
    
# API Detail barang
@admin_route.route("/api/data/barang", methods=["GET", "POST"])
@khusus_admin
def dataBarang():
    # Ambil data pemesanan
    detailBarang = collection["data_barang"]
    try:
        if request.method == "POST":
            return respon_api("error", 400, "Bad request", [], {}), 400
            
        else:
            idBarang = request.args.get("id_barang")
            if idBarang:
                # Ambil data barang
                return tampilkanDataSpesifik(detailBarang, idBarang)
            else:
                return respon_api("error", 400, "Bad request", [], {}), 400

    except Exception as error:
        return respon_api("error", 500, str(error), [], {}), 500

# Invoice
@admin_route.route("/api/data/invoice", methods=["GET", "POST"])
@khusus_admin
def kelolaInvoice():
    try:
        data_invoice = collection["invoice"]

        if request.method == "POST":
            return respon_api("error", 400, "Bad request", [], {}), 400
        else:
            withPemesanan = request.args.get("with_pemesanan")

            if withPemesanan:
                halaman = int(request.args.get("page", 1))
                batas = int(request.args.get("limit", 10))
                lewati = (halaman - 1) * batas

                total_items = data_invoice.count_documents({})
                total_halaman = math.ceil(total_items / batas)

                cursor = data_invoice.find().sort("_id", -1).skip(lewati).limit(batas)
                data = []
                for barisData in cursor:
                    dataPemesanan = collection["pemesanan_kargo"].find_one({"_id": ObjectId(barisData["pemesanan_id"])})
                    dataPelanggan = collection["data_pelanggan"].find_one({"_id": ObjectId(barisData["pelanggan_id"])})

                    data.append({
                        "_id": str(barisData["_id"]),
                        "kode_invoice": barisData["kode_invoice"],
                        "pemesanan": convert_objectid_to_str(dataPemesanan),
                        "pelanggan": convert_objectid_to_str(dataPelanggan),
                        "metode_pembayaran": barisData["metode_pembayaran"],
                        "status_pembayaran": barisData["status_pembayaran"],
                        "rincian_pembayaran": barisData["rincian_pembayaran"],
                        "catatan": barisData["catatan"],
                        "updated_at": barisData["updated_at"]
                    })

                if data:
                    pageTest = {
                        "current_page": halaman,
                        "per_page": batas,
                        "total_items": total_items,
                        "total_pages": total_halaman
                    }

                    return respon_api("success", 200, "Data tersedia", data, pageTest)
                else:
                    return respon_api("success", 200, "Data tidak tersedia", [], {})

            else:
                return tampilkanSemuaData(data_invoice, request.args.get("page", 1), request.args.get("limit", 10), {}, {})

    except Exception as error:
        return respon_api("error", 500, str(error), [], {})

# Kelola users
@admin_route.route("/api/data/users", methods=["GET", "POST"])
@khusus_admin
def dataUsers():
    try:
        data_users = collection["users"]
        if request.method == "GET":
            if "role" in request.args:
                role = str(request.args["role"])
                return tampilkanSemuaData(data_users, request.args.get("page", 1), request.args.get("limit", 10), {"role": role}, {"password": 0})
            else:
                return respon_api("error", 400, "Bad request", [], {}), 400

    except Exception as error:
        return respon_api("error", 500, str(error), [], {})
    
# Kelola data pelanggan
@admin_route.route("/api/data/pelanggan", methods=["GET", "POST"])
@khusus_admin
def dataPelanggan():
    try:
        data_pelanggan = collection["data_pelanggan"]
        if request.method == "GET":
            if "id" in request.args:
                idPelanggan = str(request.args["id"])
                return tampilkanDataSpesifik(data_pelanggan, idPelanggan)
            else:
                return respon_api("error", 400, "Bad request", [], {}), 400

    except Exception as error:
        return respon_api("error", 500, str(error), [], {})
    
# Kategori Barang Kargo
@admin_route.route("/api/data/kategori", methods=["GET", "POST"])
@khusus_admin
def dataKategori():
    kategori_barang = collection["kategori_barang_kargo"]
    try:
        if request.method == "POST":
            return tampilkanSemuaData(kategori_barang, request.args.get("page", 1), request.args.get("limit", 10), {}, {})
        
        else:
            kategoriId = request.args.get("kategori_id")
            if kategoriId:
                return tampilkanDataSpesifik(kategori_barang, ObjectId(kategoriId))
            else:
                return tampilkanSemuaData(kategori_barang, request.args.get("page", 1), request.args.get("limit", 10), {}, {})

    except Exception as error:
        return respon_api("error", 500, str(error), [], {})

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
                return tampilkanSemuaData(tarif, request.args.get("page", 1), request.args.get("limit", 10), {}, {})

    except Exception as error:
        return respon_api("error", 500, str(error), [], {}), 500
    
# Keluhan pelanggan
@admin_route.route("/api/data/feedback", methods=["GET", "POST", "DELETE"])
@khusus_admin
def dataFeedback():
    try:
        feedback = collection["feedback"]
        
        if request.method == "POST":
            data_json = request.get_json()

            if data_json and data_json.get("markRead"):
                markRead = str(data_json.get("markRead"))

                if feedback.update_one({"_id": ObjectId(markRead)}, {"$set": {"dibaca": True}}):
                    return respon_api("success", 200, "Keluhan ditandai dibaca", [], {})
                else:
                    return respon_api("error", 500, "Terjadi kesalahan", [], {}), 500

            else:
                if feedback.update_many({}, {"$set": {"dibaca": True}}):
                    return respon_api("success", 200, "Semua keluhan ditandai sudah dibaca", [], {})
                else:
                    return respon_api("error", 500, "Terjadi kesalahan", [], {}), 500

        elif request.method == "DELETE":
            data_json = request.get_json()

            if feedback.delete_one({"_id": ObjectId(data_json.get("delete"))}):
                return respon_api("success", 200, "Keluhan berhasil dihapus", [], {})
            else:
                return respon_api("error", 500, "Gagal menghapus keluhan", [], {}), 500

        # Request method GET
        else:
            if "unread" in request.args:
                query = {
                    "$or": [
                        {"dibaca": False},
                        {"dibaca": {"$exists": False}}
                    ]
                }

                hitung = feedback.count_documents(query)

                if hitung > 0:
                    return respon_api("success", 200, "Ada keluhan yang belum dibaca", {"unread": hitung}, {})
                else:
                    return respon_api("success", 200, "Tidak ada keluhan yang belum dibaca", [], {}), 200
            else:
                return tampilkanSemuaData(feedback, request.args.get("page", 1), request.args.get("limit", 10), {}, {})

    except Exception as error:
        return respon_api("error", 500, str(error), [], {})

# Experiment
@admin_route.route("/register", methods=["GET", "POST"])
def register():
    return render_template("admin/auth/regist.html")

@admin_route.route("/send-test-email", methods=["POST"])
def send_test_email():
    data = request.get_json(silent=True) or {}
    recipient = data.get("to", "test@example.com")

    # Data dinamis untuk template
    context = {
        "USER_NAME": data.get("name", "Pelanggan BCE Cargo"),
        "APP_NAME": data.get("app_name", "BCE Cargo"),
        "CODE": data.get("code", "123456"),
        "EXP_MINUTES": data.get("expired", "5"),
        "SUPPORT_EMAIL": data.get("email_support", "support@bcecargo.com"),
        "YEAR": datetime.now().year
    }

    # Render template Jinja (HTML & plain-text)
    html_body = render_template("emails/verif.html", **context)
    text_body = render_template("emails/verif.txt", **context)

    send_email_smtp(
        host=current_app.config["MAIL_SERVER"],
        port=current_app.config["MAIL_PORT"],
        sender=current_app.config["MAIL_SENDER"],
        to=recipient,
        subject=f"Kode verifikasi akun anda adalah " + data.get("code", "123456"),
        html_body=html_body,
        text_body=text_body
    )

    return respon_api("success", 200, "Email sent to: " + recipient, [], {})
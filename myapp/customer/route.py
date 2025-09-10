from flask import Blueprint, jsonify, request,render_template, session, redirect, url_for, current_app
from connection import db_bce
from pymongo import ReturnDocument
from functools import wraps
from datetime import datetime, timedelta, timezone
import bcrypt, math, requests, json
from myapp.customer.generate_code import generate_verification_code
from bson.objectid import ObjectId
from myapp.email_utils import send_email_smtp

# Collection
collection = db_bce.use_db()
userData = collection["users"]

# API
# Convert _id
def convert_objectid_to_str(doc):
    # Conver "_id"
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])

    # Convert "user_id"
    if 'user_id' in doc:
        doc['user_id'] = str(doc['user_id'])

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

# Buat kode pemesanan
def generate_kode_pemesanan(moda: str) -> str:
    counters = collection["counters"]
    
    # mapping moda pake match-case
    match moda.lower():
        case "udara":
            moda_code = "U"
        case "darat":
            moda_code = "D"
        case "laut":
            moda_code = "L"
        case _:
            raise ValueError("Moda tidak dikenal. Gunakan: Udara, Darat, atau Laut.")

    # format tanggal: yymmdd
    tanggal = datetime.now().strftime("%y%m%d")

    # bikin key unik berdasarkan moda + tanggal
    key = f"{moda_code}-{tanggal}"

    # update counter di MongoDB (atomic operation)
    doc = counters.find_one_and_update(
        {"id": key},
        {"$inc": {"sequence_value": 1}},
        upsert=True,  # kalau belum ada, buat baru
        return_document=ReturnDocument.AFTER
    )

    # ambil nomor urut
    urutan = doc["sequence_value"]
    unique_id = f"{urutan:03}"  # jadi 3 digit

    return f"BCE-{moda_code}-{tanggal}-{unique_id}"

# Ubah UTC ke Indonesia
def convert_utc_to_indonesia(waktu):
    # Mengubah waktu UTC ke waktu Indonesia (WIB, UTC+7)
    indonesia_time = waktu.astimezone(timezone(timedelta(hours=7)))
    
    # Mengembalikan format tanggal dan waktu
    return indonesia_time.strftime('%d %B %Y, %H:%M:%S WIB')

# Tampilkan Data Spesifik
def tampilkanDataSpesifik(koleksi, query):
    data = koleksi.find_one(query)
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

# Fetch wilayah indonesia
def fetchIndo(jenisWilayah, idWilayah, parentWilayah = None):
    url = ""

    match jenisWilayah:
        case "provinsi":
            url = f"https://emsifa.github.io/api-wilayah-indonesia/api/provinces.json"
        case "kabupaten":
            url = f"https://emsifa.github.io/api-wilayah-indonesia/api/regencies/{parentWilayah}.json"
        case "kecamatan":
            url = f"https://www.emsifa.com/api-wilayah-indonesia/api/districts/{parentWilayah}.json"
        case "kelurahan":
            url = f"https://www.emsifa.com/api-wilayah-indonesia/api/villages/{parentWilayah}.json"

    try:
        wilayah = requests.get(url)
        wilayah = wilayah.json()

        for listWilayah in wilayah:
            if listWilayah["id"] == idWilayah:
                dataWilayah = {
                    "id": int(listWilayah["id"]),
                    "name": str(listWilayah["name"])
                }

                return dataWilayah
    except Exception as error:
        return print(error)

# Atur route
customer_route = Blueprint("customer", __name__)

@customer_route.context_processor
def inject_globals():
    return dict(
        nama_pengguna=session.get("name"),
        email_pengguna=session.get("email"),
        role_pengguna=session.get("role"),
        active_page=None,  # ini bisa dioverride di masing-masing route
        current_time=datetime.now(timezone.utc)
    )

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
    bioPelanggan = collection["data_pelanggan"]
    sudahRegister = bioPelanggan.find_one({"user_id": ObjectId(session["user_id"])}, {"user_id": 1})
    if sudahRegister:
        return render_template("customer/pages/pesanan.html")
    else:
        return(redirect(url_for("customer.pendaftaran")))

#PROFILE
@customer_route.route("/profile", methods=["GET", "POST"])
@khusus_customer
def profile():
    bioPelanggan = collection["data_pelanggan"]
    sudahRegister = bioPelanggan.find_one({"user_id": ObjectId(session["user_id"])}, {"user_id": 1})
    if sudahRegister:
        return render_template("customer/pages/profile.html")
    else:
        return(redirect(url_for("customer.pendaftaran")))

#PENDAFTARAN
@customer_route.route("/pendaftaran", methods=["GET", "POST"])
@khusus_customer
def pendaftaran():
    bioPelanggan = collection["data_pelanggan"]
    sudahRegister = bioPelanggan.find_one({"user_id": ObjectId(session["user_id"])}, {"user_id": 1})
    print(sudahRegister)
    if sudahRegister:
        return redirect(url_for("home"))
    else:
        return render_template("customer/pages/pendaftaran.html")

# RIWAYAT PESANAN
@customer_route.route("/riwayat", methods=["GET", "POST"])
@khusus_customer
def riwayat():
    bioPelanggan = collection["data_pelanggan"]
    sudahRegister = bioPelanggan.find_one({"user_id": ObjectId(session["user_id"])}, {"user_id": 1})
    if sudahRegister:
        return render_template("customer/pages/riwayat.html")
    else:
        return(redirect(url_for("customer.pendaftaran")))

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
# Data akun Pengguna
@customer_route.route("/api/data/account", methods=["GET","POST"])
@khusus_customer
def dataAkunPelanggan():
    try:
        if request.method == "POST":
            uid = request.args.get("uid")
            return tampilkanDataSpesifik(userData, uid)
    
        # request GET (default)
        else:
            return tampilkanDataSpesifik(userData, {"_id": ObjectId(session["user_id"])})
    except Exception as error:
        return respon_api("error", 500, "Terjadi kesalahan", str(error), {}), 500
    

# Data akun Pengguna
@customer_route.route("/api/data/pelanggan", methods=["GET","POST"])
@khusus_customer
def dataPelanggan():
    try:
        biopelanggan = collection["data_pelanggan"]
        if request.method == "POST":
            # update biodata pelanggan jika pelanggan baru mendaftar
            if "daftarPelanggan" in request.form:
                # Biodata
                namaLengkap = str(request.form["nama"])
                noTelp = str(request.form["ponsel"])
                jenisPelanggan = str(request.form["jenis"])
                perusahaan = str(request.form.get("perusahaan", ""))

                # Alamat
                jalan = str(request.form["jalan"])
                noRumah = str(request.form["no_rumah"])
                kodepos = str(request.form["kodepos"])
                rt = str(request.form["rt"])
                rw = str(request.form["rw"])

                # Wilayah Indonesia
                provinsi = str(request.form["provinsi"])
                kabupaten = str(request.form["kabupaten"])
                kecamatan = str(request.form["kecamatan"])
                kelurahan = str(request.form["kelurahan"])

                DataPelanggan = {
                    "user_id": ObjectId(session["user_id"]),
                    "nama_lengkap": namaLengkap,
                    "alamat": {
                        "jalan": jalan,
                        "no_rumah": noRumah,
                        "rt": rt,
                        "rw": rw,
                        "kelurahan": fetchIndo("kelurahan", kelurahan, kecamatan),
                        "kecamatan": fetchIndo("kecamatan", kecamatan, kabupaten),
                        "kabupaten": fetchIndo("kabupaten", kabupaten, provinsi),
                        "provinsi": fetchIndo("provinsi", provinsi),
                        "kode_pos": kodepos
                    },
                    "no_telepon": noTelp,
                    "jenis_pelanggan": jenisPelanggan,
                    "nama_perusahaan": perusahaan,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
                
                if biopelanggan.insert_one(DataPelanggan):
                    return respon_api("success", 200, "Pendaftaran berhasil", [], {})
                else:
                    return respon_api("error", 500, "Terjadi kesalahan saat mendaftar", [], {}), 500

    
        # request GET (default)
        else:
            return tampilkanDataSpesifik(biopelanggan, {"user_id": ObjectId(session["user_id"])})
    
    except Exception as error:
        return respon_api("error", 500, "Terjadi kesalahan", str(error), {}), 500

# Pemesanan
@customer_route.route("/api/data/kategori_barang", methods=["GET"])
@khusus_customer
def kategoriBarang():
    print("Ok")
    cursor = collection["kategori_barang_kargo"].find({})
    data = [convert_objectid_to_str(doc) for doc in cursor]

    if data:
        return respon_api("success", 200, str("Data tersedia"), data, {})
    else:
        return respon_api("error", 404, str("Data tidak tersedia"), [], {}), 404
    
@customer_route.route("/api/pemesanan", methods=["GET", "POST"])
@khusus_customer
def pemesanan():
    try:
        if request.method == "POST":
            dataPemesan = collection["data_pelanggan"].find_one({"user_id": ObjectId(session["user_id"])})

            # Biodata pengirim
            namaPengirim = str(request.form["nama_pengirim"])
            noPengirim = str(request.form["whatsapp_pengirim"])

            jalanPengirim = str(request.form["jalan_pengirim"])
            kodeposPengirim = str(request.form["kodepos_pengirim"])
            rtPengirim = str(request.form["rt_pengirim"])
            rwPengirim = str(request.form["rw_pengirim"])

            provinsiPengirim = str(request.form["provinsi_pengirim"])
            kabupatenPengirim = str(request.form["kabupaten_pengirim"])
            kecamatanPengirim = str(request.form["kecamatan_pengirim"])
            kelurahanPengirim = str(request.form["kelurahan_pengirim"])

            alamatLengkapPengirim = "Jl. " + jalanPengirim + ", " + "Rt. " + rtPengirim + ", " + "Rw. " + rwPengirim + ", " + "Kel. " + fetchIndo("kelurahan", kelurahanPengirim, kecamatanPengirim)["name"] + ", " + "Kec. " + fetchIndo("kecamatan", kecamatanPengirim, kabupatenPengirim)["name"] + ", " + "Kab. " + fetchIndo("kabupaten", kabupatenPengirim, provinsiPengirim)["name"] + ", " + "Prov. " + fetchIndo("provinsi", provinsiPengirim)["name"] + ", " + "Kode pos. " + kodeposPengirim

            # Biodata Penerima
            namaPenerima = str(request.form["nama_penerima"])
            noPenerima = str(request.form["whatsapp_penerima"])

            jalanPenerima = str(request.form["jalan_penerima"])
            kodeposPenerima = str(request.form["kodepos_penerima"])
            rtPenerima = str(request.form["rt_penerima"])
            rwPenerima = str(request.form["rw_penerima"])

            provinsiPenerima = str(request.form["provinsi_penerima"])
            kabupatenPenerima = str(request.form["kabupaten_penerima"])
            kecamatanPenerima = str(request.form["kecamatan_penerima"])
            kelurahanPenerima = str(request.form["kelurahan_penerima"])

            alamatLengkapPenerima = "Jl. " + jalanPenerima + ", " + "Rt. " + rtPenerima + ", " + "Rw. " + rwPenerima + ", " + "Kel. " + fetchIndo("kelurahan", kelurahanPenerima, kecamatanPenerima)["name"] + ", " + "Kec. " + fetchIndo("kecamatan", kecamatanPenerima, kabupatenPenerima)["name"] + ", " + "Kab. " + fetchIndo("kabupaten", kabupatenPenerima, provinsiPenerima)["name"] + ", " + "Prov. " + fetchIndo("provinsi", provinsiPenerima)["name"] + ", " + "Kode pos. " + kodeposPenerima

            # Data barang
            listBarang = []
            dataBarang = json.loads(request.form["data_barang"])
            global modaBarang
            global beratKargo
            beratKargo = 0
        
            for barang in dataBarang:
                idBarang = ObjectId()

                DataBarang = {
                    "_id": idBarang,
                    "nama_barang": str(barang["nama_barang"]),
                    "jumlah": int(barang["jumlah_barang"]),
                    "berat_kg": float(barang["berat_barang"]),
                    "dimensi_cm": {
                        "panjang": float(barang["panjang"]),
                        "lebar": float(barang["lebar"]),
                        "tinggi": float(barang["tinggi"])
                    },
                    "kategori_id": ObjectId(barang["kategori_barang"]),
                    "butuh_asuransi": bool(barang["butuh_asuransi"]),
                    "metode_pengiriman": str(barang["metode_pengiriman"]),
                    "catatan_tambahan": str(barang["catatan_barang"]),
                    "status_cek_dg": "belum dicek",
                    "biaya_surcharge": None,
                    "butuh_packing_khusus": False,
                    "butuh_label_dg": False
                }

                # Kirim data barang ke DB
                collection["data_barang"].insert_one(DataBarang)

                listBarang.append(idBarang)
                beratKargo = beratKargo + float(barang["berat_barang"])
                modaBarang = str(barang["metode_pengiriman"])

            kodePesanan = generate_kode_pemesanan(modaBarang)
            # Data pesanan
            DataPesanan = {
                "_id": ObjectId(),
                "kode_pemesanan": kodePesanan,
                "nama_pengirim": namaPengirim,
                "nama_penerima": namaPenerima,
                "alamat_pengirim": alamatLengkapPengirim,
                "alamat_penerima": alamatLengkapPenerima,
                "no_hp_pengirim": noPengirim,
                "no_hp_penerima": noPenerima,
                "jenis_kargo": modaBarang,
                "berat_kargo": beratKargo,
                "harga_total": 0,
                "status": "Pending",
                "tanggal_pemesanan": datetime.now(timezone.utc),
                "pelanggan_id": dataPemesan["_id"],
                "barang_ids": listBarang
            }

            buatPesanan = collection["pemesanan_kargo"].insert_one(DataPesanan)

            # Kirim email ke setiap admin
            if buatPesanan:
                ambilEmailAdmin = collection["users"].find({"role": "admin"}, {"email": 1})
                listEmailAdmin = [listEmail["email"] for listEmail in ambilEmailAdmin]

                # Bagian kirm email
                # Data untuk template
                context = {
                    "kode_pemesanan": kodePesanan,
                    "nama_pengirim": namaPengirim,
                    "no_hp_pengirim": noPengirim,
                    "alamat_pengirim": alamatLengkapPengirim,
                    "nama_penerima": namaPenerima,
                    "no_hp_penerima": noPenerima,
                    "alamat_penerima": alamatLengkapPenerima,
                    "jenis_kargo": modaBarang,
                    "berat_kargo": beratKargo,
                    "tanggal_pemesanan": convert_utc_to_indonesia(datetime.now(timezone.utc)),
                    "ADMIN_DASHBOARD_URL": f"http://localhost:5000/admin/pesanan_masuk",
                    "APP_NAME": "CV. Bahtera Cahaya Express"
                }

                html_body = render_template("emails/admin/pesan_baru.html", **context)
                text_body = render_template("emails/admin/pesan_baru.txt", **context)

                # Hanya 1 kali kirim dengan BCC
                send_email_smtp(
                    host=current_app.config["MAIL_SERVER"],
                    port=current_app.config["MAIL_PORT"],
                    sender=current_app.config["MAIL_SENDER"],
                    to="no-reply@bce-cargo.local",  # placeholder
                    subject=f"Pesanan Baru #{kodePesanan}",
                    html_body=html_body,
                    text_body=text_body,
                    bcc=listEmailAdmin
                )

            return respon_api("success", 200, str("Data terkirim"), [], {})
        else:
            return respon_api("error", 400, "Bad request", [], {}), 400
        
    except Exception as error:
        return respon_api("error", 500, str(error), [], {}), 500


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
                    return respon_api("error", 401, "Sandi salah", [], {}), 401
            else:
                return respon_api("error", 401, "Akun tidak tersedia", [], {}), 401

        # Sistem Registrasi
        if "register" in request.form:
            email = str(request.form["email"])
            password = request.form["confirm_password"]
            fullname = str(request.form["fullname"])

            # Cek akun customer
            akun = userData.find_one({"email": email, "role": "customer"})
            if akun: 
                return respon_api("error", 409, "Email Sudah Terdaftar", [], {}), 409
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
        return respon_api("error", 500, str(error), [], {}), 500
    
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
                return respon_api("error", 401, "Kode Salah", [], {}), 401
        else:
            return respon_api("error", 401, "Akun tidak tersedia", [], {}), 401
    
    except Exception as error:
        return respon_api("error", 500, str(error), [], {}), 500
    
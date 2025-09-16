from flask import Flask, render_template, jsonify, request, redirect, url_for, session, send_from_directory
from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv
import os, requests, json

# Load .env
load_dotenv()

# .env Variable
SESSION_KEY = os.getenv("SESSION_KEY")

# Import blueprint
# Admin (Fatah)
from myapp.admin.route import admin_route

# Customer (Galang)
from myapp.customer.route import customer_route

# Chatbot (Fadel)
from myapp.chatbot.route import chatbot_route

app = Flask(__name__)
app.secret_key = SESSION_KEY
app.permanent_session_lifetime = timedelta(days=30)

# Konfigurasi MailHog (lokal)
app.config.update(
  MAIL_SERVER='localhost',
  MAIL_PORT=1025,
  MAIL_SENDER='no-reply@bcecargo.com' # hanya label; tidak betul-betul terkirim
)

# Cek masa sesi login user
@app.before_request
def cek_masa_sesi():
  kedaluwarsa = session.get("kedaluwarsa")
  role = session.get("role")
  
  if kedaluwarsa:
    waktu_sekarang = datetime.now(timezone.utc)
    waktu_kedaluwarsa = datetime.fromisoformat(kedaluwarsa)

    if waktu_sekarang > waktu_kedaluwarsa:
      session.clear()

      if role == "admin":
        redirect(url_for("admin.login"))
      else:
        redirect(url_for("customer.login"))

    # Perpanjang sesi jika ada aktifitas (hanya untuk admin)
    if role == "admin":
      session['kedaluwarsa'] = (waktu_sekarang + timedelta(hours=1)).isoformat()


# Import node modules
@app.route("/node_modules/<path:filename>")
def serve_node_modules(filename):
  return send_from_directory("node_modules", filename)

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

# Blueprint
# Admin (Fatah)
app.register_blueprint(admin_route, url_prefix="/admin/")

# Customer Pages (Galang)
app.register_blueprint(customer_route, url_prefix="/customer/")

# Chatbot (Fadel)
app.register_blueprint(chatbot_route, url_prefix="/chatbot/")

# Home pages
@app.route('/')
def home():
  return render_template('index.html')

# Provinsi
@app.route("/api/data/provinsi")
def get_provinsi():
    try:
        url = "https://emsifa.github.io/api-wilayah-indonesia/api/provinces.json"
        response = requests.get(url)
        return respon_api("success", 200, "Fetch berhasil", response.json(), {})
    
    except Exception as error:
        return respon_api("error", 500, str(error), [], {})

# Kabupaten
@app.route("/api/data/kabupaten/<prov_id>")
def get_kabupaten(prov_id):
    try:
        url = f"https://emsifa.github.io/api-wilayah-indonesia/api/regencies/{prov_id}.json"
        response = requests.get(url)
        return respon_api("success", 200, "Fetch berhasil", response.json(), {})
    
    except Exception as error:
        return respon_api("error", 500, str(error), [], {})
    
# Kecamatan
@app.route("/api/data/kecamatan/<kab_id>")
def get_kecamatan(kab_id):
    try:
        url = f"https://www.emsifa.com/api-wilayah-indonesia/api/districts/{kab_id}.json"
        response = requests.get(url)
        return respon_api("success", 200, "Fetch berhasil", response.json(), {})
    
    except Exception as error:
        return respon_api("error", 500, str(error), [], {})

# Kelurahan
@app.route("/api/data/kelurahan/<kec_id>")
def get_kelurahan(kec_id):
    try:
        url = f"https://www.emsifa.com/api-wilayah-indonesia/api/villages/{kec_id}.json"
        response = requests.get(url)
        return respon_api("success", 200, "Fetch berhasil", response.json(), {})
    
    except Exception as error:
        return respon_api("error", 500, str(error), [], {})
    
@app.route("/api/data/kode_kota", methods=["GET"])
def kodeKota():
    try:
      with open("static/json/kode_kota.json", "r") as f:
        data = json.load(f)
        return respon_api("success", 200, "JSON Data loaded successfull", data, {})
    
    except Exception as e:
      return respon_api("error", 500, str(e), [], {}), 500
    
# Uji coba tampilan email (hapus bagian ini setelah produksi)
@app.route("/email_test")
def email_test():
   return render_template("emails/penolakan_pesanan.html")

if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)

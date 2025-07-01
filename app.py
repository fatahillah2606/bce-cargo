from flask import Flask, render_template, jsonify, request, redirect, url_for, session, send_from_directory
from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv
import os

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
app.permanent_session_lifetime = timedelta(hours=1)

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

# if __name__ == '__main__':
#   app.run(debug=True)
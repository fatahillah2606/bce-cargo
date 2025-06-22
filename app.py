from flask import Flask, render_template, jsonify, request, redirect, url_for, session, send_from_directory
from connection import db_bce

# Import blueprint
# Admin (Fatah)
from myapp.admin.route import admin_route

# Customer (Galang)
from myapp.customer.route import customer_route

# Chatbot (Fadel)
from myapp.chatbot.route import chatbot_route

app = Flask(__name__)

# Import node modules
@app.route("/node_modules/<path:filename>")
def serve_node_modules(filename):
    return send_from_directory("node_modules", filename)

# Collection
collection = db_bce.use_db()
data_chatbot = collection["chatbot"]

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
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, send_from_directory
from connection import db_bce

app = Flask(__name__)

# Import node modules
@app.route("/node_modules/<path:filename>")
def serve_node_modules(filename):
    return send_from_directory("node_modules", filename)

# Collection
collection = db_bce.use_db()
data_chatbot = collection["chatbot"]


# Customer Pages (Galang)
# Home pages
@app.route('/')
def home():
  return render_template('index.html')

# Admin Pagses (Fatah)
@app.route("/admin")
def admin():
   return render_template('admin/index.html')

# Chatbot (Fadel)
@app.route('/chatbot')
def chatbot():
  return render_template('chatbot/chatbot.html')

# Perintah untuk chatbot
@app.route('/commands')
def get_commands():
    commands = list(data_chatbot.find({}, {"_id": 0}))
    return jsonify(commands)

# if __name__ == '__main__':
#   app.run(debug=True)
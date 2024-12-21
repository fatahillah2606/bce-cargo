from http import client
import json
from flask import Flask, render_template, send_file, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Test koneksi ke database
uri = "mongodb://localhost:27017/"
client = MongoClient(uri)
db = client["bce-cargo"]
collection = db["chatbot"]

# Home pages
@app.route('/')
def home():
  return render_template('index.html')

# Chatbot Fadel
@app.route('/chatbot')
def chatbot():
  return render_template('Test Chatbot (Alpha Test 1.0)/chatbot.html')

# Perintah untuk chatbot
@app.route('/commands')
def get_commands():
    commands = list(collection.find({}, {"_id": 0}))
    return jsonify(commands)

# Info perusahaan untuk chatbot
@app.route('/botinfo')
def botinfo():
  return send_file('app/botinfo.txt', mimetype='text/plain')

if __name__ == '__main__':
  app.run(debug=True)
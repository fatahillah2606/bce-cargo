from flask import Flask, render_template, jsonify
from connection import db_bce

app = Flask(__name__)

# Collection
collection = db_bce.use_db()
data_chatbot = collection["chatbot"]

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
    commands = list(data_chatbot.find({}, {"_id": 0}))
    return jsonify(commands)

# if __name__ == '__main__':
#   app.run(debug=True)
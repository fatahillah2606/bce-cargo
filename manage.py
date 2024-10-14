from flask import Flask, render_template, send_file

app = Flask(__name__)

# Home pages
@app.route('/')
def home():
  return render_template('index.html')

# Chatbot Fadel
@app.route('/chatbot')
def chatbot():
  return render_template('Test Chatbot (Alpha Test 1.0)/chatbot.html')

# Info perusahaan untuk chatbot
@app.route('/botinfo')
def botinfo():
  return send_file('app/botinfo.txt', mimetype='text/plain')

if __name__ == '__main__':
  app.run(debug=True)
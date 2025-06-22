from flask import Blueprint, jsonify, request, render_template
from connection import db_bce

# Collection
collection = db_bce.use_db()
data_chatbot = collection["chatbot"]

# Atur route
chatbot_route = Blueprint("chatbot", __name__)

# Route
@chatbot_route.route("/", methods=["GET", "POST"])
def chatbot():
    return render_template('chatbot/chatbot.html')

@chatbot_route.route("/commands", methods=["GET", "POST"])
def commands():
    commands = list(data_chatbot.find({}, {"_id": 0}))
    return jsonify(commands)
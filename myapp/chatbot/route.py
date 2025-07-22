from flask import Blueprint, jsonify, request, render_template
from connection import db_bce
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# .env Variable
AI_AGENT = os.getenv("AI_AGENT")

# Collection
collection = db_bce.use_db()
data_chatbot = collection["chatbot"]

# Atur route
chatbot_route = Blueprint("chatbot", __name__)

# Respon API
def respon_api(status, code, message, data):
    respon = {
        "status": status,
        "code": code,
        "message": message,
        "data": data if data else []
    }
    return jsonify(respon)

# Route
@chatbot_route.route("/", methods=["GET", "POST"])
def chatbot():
    return render_template('chatbot/base.html')

@chatbot_route.route("/commands", methods=["GET", "POST"])
def commands():
    commands = list(data_chatbot.find({}, {"_id": 0}))
    return jsonify(commands)

@chatbot_route.route("/agent", methods=["GET", "POST"])
def agent():
    return respon_api("success", 200, "Agent terhubung", {"agentlinked": AI_AGENT})

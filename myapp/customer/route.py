from flask import Blueprint, jsonify, request, render_template

# Atur route
customer_route = Blueprint("customer", __name__)

# Route
@customer_route.route("/", methods=["GET", "POST"])
@customer_route.route("/login", methods=["GET", "POST"])
def login():
    return render_template("customer/login.html")

# Uji coba hal baru
@customer_route.route("/cv_baru", methods=["GET", "POST"])
def cv_baru():
    return render_template("new.html")
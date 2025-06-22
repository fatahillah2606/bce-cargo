from flask import Blueprint, jsonify, request, render_template

# Atur route
admin_route = Blueprint("admin", __name__)

# Route
@admin_route.route("/", methods=["GET", "POST"])
def login():
    return render_template("admin/index.html")

@admin_route.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    return render_template("admin/dashboard.html")
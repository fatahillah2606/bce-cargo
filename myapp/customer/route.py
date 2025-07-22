from flask import Blueprint, jsonify, request, render_template

# Atur route
customer_route = Blueprint("customer", __name__)

# Route
@customer_route.route("/", methods=["GET", "POST"])

# LOGIIN
@customer_route.route("/login", methods=["GET", "POST"])
def login():
    return render_template("customer/login.html")

# REGISTER
@customer_route.route("/register", methods=["GET", "POST"])
def register():
    return render_template("customer/register.html")

#PENGECEKAN
@customer_route.route("/pengecekan", methods=["GET", "POST"])
def pengecekan():
    return render_template("customer/pengecekan.html")

# ONGKIR
@customer_route.route("/ongkir", methods=["GET", "POST"])
def ongkir():
    return render_template("customer/ongkir.html")

# PESANAN
@customer_route.route("/pesanan", methods=["GET", "POST"])
def pesanan():
    return render_template("customer/pesanan.html")



# Uji coba hal baru
@customer_route.route("/cv_baru", methods=["GET", "POST"])
def cv_baru():
    return render_template("new.html")
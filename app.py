import mysql.connector, functools, requests
import json
from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, session

app = Flask(__name__)

# Έλεγχος του authentication
def check_credentials(username, password):
    try:
        # Σύνδεση στη βάση δεδομένων MySQL
        conn = mysql.connector.connect(
            host="localhost", user="root", password="", database="login"
        )
        cursor = conn.cursor()

        # Εκτέλεση ερωτήματος SQL για τον έλεγχο του username και password
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))

        # Λήψη των αποτελεσμάτων του ερωτήματος
        user = cursor.fetchone()

        # Κλείσιμο της σύνδεσης με τη βάση δεδομένων
        conn.close()

        # Έλεγχος αν βρέθηκε ο χρήστης στη βάση δεδομένων
        if user:
            return True
        else:
            return False
    except mysql.connector.Error as err:
        print(f"Σφάλμα σύνδεσης στη βάση δεδομένων: {err}")
        return False

app.secret_key = "my_test_app"

def login_required(view):
    @functools.wraps(view)
    def check(*args, **kwargs):
        if "username" in session:
            return view(*args, **kwargs)
        else:
            return redirect(url_for("login"))

    return check


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        # Έλεγχος του username και password που πληκτρολόγησε ο χρήστης
        username = request.form["username"]
        password = request.form["password"]
        # Εκτελείται η σύνδεση του χρήστη και αποθηκεύεται στην session
        if check_credentials(username, password):
            session["username"] = username
            return redirect(url_for("home"))
        message = "Λάθος στοιχεία"

    return render_template("login.html", message=message)


@app.route("/logout")
def logout():
    # Αποσύνδεση του χρήστη με διαγραφή της session
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/")
@login_required
def home():
    username=session["username"]
    return render_template("home.html", username=username)


@app.route("/products")
@login_required
def products():
    # Λήψη των προϊόντν απο το εξωτερικό endpoint
    url = "https://cloudonapi.oncloud.gr/s1services/JS/updateItems/cloudOnTest"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print("Η αίτηση απέτυχε με κωδικό:", response.status_code)

    if data is not None and "data" in data:
        return render_template("products.html", products=data["data"])
    else:
        return render_template("products.html", products=[])


@app.route("/newProduct")
@login_required
def newProduct():
    return render_template("newProduct.html")

@app.route("/editProduct/<string:external_id>")
@login_required
def editProduct(external_id):
    # Λήψη και εύρεση προϊόντος προς επεξεργασία
    print(external_id)
    url = "https://cloudonapi.oncloud.gr/s1services/JS/updateItems/cloudOnTest"
    response = requests.get(url)
    data = response.json()
    prod = None
    for i in data["data"]: 
        if external_id == i["externalId"]:
            prod = i
    return render_template("editProduct.html", prod=prod)

if __name__ == "__main__":
    app.run(debug=True, port=5500)

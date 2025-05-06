from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os

from models.user import User

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password") or ""
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)

            try:
                external_url = (os.getenv("MS2_BOOKSTORE_URI") or "") + "/set-current"
                payload = {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                }
                response = requests.post(external_url, json=payload, timeout=5)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error sending user to external server: {e}")

            return redirect(url_for("home"))
        else:
            flash("Login failed")
    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        new_user = User()
        new_user.name = name
        new_user.email = email
        new_user.password = generate_password_hash(password, method="pbkdf2:sha256")
        db.session.add(new_user)
        db.session.commit()

        try:
            external_url = (os.getenv("MS2_BOOKSTORE_URI") or "") + "/create"
            payload = {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email,
            }
            response = requests.post(external_url, json=payload, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error sending user to external server: {e}")

        return redirect(url_for("auth.login"))
    return render_template("register.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

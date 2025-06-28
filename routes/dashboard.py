from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@bp.route("/", methods=["GET", "POST"])
def index():
    if "usuario_id" not in session:
        return redirect(url_for("login.index"))
    email_usuario = session["email"]
    return render_template("dashboard.html", email=email_usuario)
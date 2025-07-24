from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
import bcrypt
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message




bp = Blueprint('login', __name__, url_prefix='/login')#Separa a rota /login

@bp.route('/', methods=['GET', 'POST'])
def index():
    from app import limiter
    #@limiter.limit("5 per minute")
    def login_func():
        mensagem = ""
        if request.method == 'POST': #Get user data
            email = request.form['email']
            senha = request.form['senha']

            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE email=?", (email,))
            usuario = cursor.fetchone()
            conn.close()

            if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario[5]):
                session['usuario_id'] = usuario[0]
                session['usuario_nome'] = usuario[3]
                session["email"] = usuario[4]
                return redirect(url_for('dashboard.index'))
            else:
                mensagem = "Email ou senha incorretos."

        return render_template('login.html', mensagem=mensagem)
    return login_func()

@bp.route("/forgot_password", methods=['GET'])
def forgot_password():
    return render_template("forgotPassword.html") 

@bp.route("/send_email", methods=['POST', 'GET'])
def send_email():
    if request.method == "POST":
        email = request.form.get("email")
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE email=?", (email,))
        user = cursor.fetchone()
        if user:
            token = generate_reset_token(email)
            reset_link = url_for('login.reset_password', token=token, _external=True)

            send_email_func(email, reset_link)

            return redirect(url_for("login.index"))
    return render_template("forgotPassword.html")

def generate_reset_token(email):
    from app import app
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return s.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, max_age=3600):
    from app import app
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=max_age)
    except Exception:
        return None
    return email

def send_email_func(to_email, reset_link):
    from app import app, mail
    subject = 'Password Reset Request'
    body = f"Click the link to reset your password: {reset_link}"
    with app.app_context():
        msg = Message(subject=subject,
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[to_email])
        msg.body = body
        mail.send(msg)
@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        return redirect(url_for('login.forgot_password'))

    if request.method == 'POST':
        new_password = request.form['newPassword']
        confirm_password = request.form['confirmNewPassword']
        if new_password != confirm_password:
            flash("Password do not match.", "danger")
            return render_template("reset_password.html")
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET senha=? WHERE email=?", (hashed, email))
        conn.commit()
        conn.close()

        flash('Your password has been updated.', 'success')
        return redirect(url_for('login.index'))

    return render_template('reset_password.html')
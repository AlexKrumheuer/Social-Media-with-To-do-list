from flask import Flask
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail

app = Flask(__name__)
app.secret_key = os.urandom(24)

limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

from routes import cadastro, login, dashboard

#Importar rotas
app.register_blueprint(cadastro.bp)
app.register_blueprint(login.bp)
app.register_blueprint(dashboard.bp)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '' #Put your email here
app.config['MAIL_PASSWORD'] = '' #Put your app google password here

mail = Mail(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
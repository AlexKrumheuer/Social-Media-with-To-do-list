from flask import Flask
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = os.urandom(24)

limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

from routes import cadastro, login, dashboard

#Importar rotas
app.register_blueprint(cadastro.bp)
app.register_blueprint(login.bp)
app.register_blueprint(dashboard.bp)

if __name__ == "__main__":
    app.run(debug=True)
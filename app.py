from flask import Flask
from routes import cadastro, login, dashboard
import os
app = Flask(__name__)
app.secret_key = os.urandom(24)

#Importar rotas
app.register_blueprint(cadastro.bp)
app.register_blueprint(login.bp)
app.register_blueprint(dashboard.bp)

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, redirect, url_for, session, request, render_template
from authlib.integrations.flask_client import OAuth
from main import oauthRegister, User
from dotenv import load_dotenv
import jinja2
import os
from datetime import timedelta
import logging
from config import CLIENT_ID, CLIENT_SECRET

# Configuração de logs para depuração
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Carregar as variáveis do arquivo .env
load_dotenv()

# Validar se CLIENT_ID e CLIENT_SECRET estão configurados
if not CLIENT_ID or not CLIENT_SECRET:
    logger.error("CLIENT_ID ou CLIENT_SECRET não estão configurados. Verifique o arquivo .env ou config.py.")
    raise ValueError("CLIENT_ID ou CLIENT_SECRET estão ausentes.")

# Configuração da aplicação Flask
app = Flask(__name__)
app.debug = True
app.secret_key = os.getenv('SECRET_KEY', 'development')  # Alterar em produção
app.permanent_session_lifetime = timedelta(hours=1)
oauth = OAuth(app)

# Registro do cliente OAuth para o SUAP
oauthRegister(
    oauth,
    name="suap",
    api_base_url="https://suap.ifrn.edu.br/api/",
    request_token_url=None,
    access_token_method="POST",
    access_token_url="https://suap.ifrn.edu.br/o/token/",
    authorize_url="https://suap.ifrn.edu.br/o/authorize/",
    token="suap_token"
)

# Manipulador de erro para UndefinedError no Jinja2
@app.errorhandler(jinja2.exceptions.UndefinedError)
def handle_jinja2_error(e):
    logger.error("Erro de template Jinja2: %s", str(e))
    return render_template('500.html', error="Erro interno no servidor."), 500

# Manipulador de erros genéricos
@app.errorhandler(Exception)
def handle_generic_error(e):
    logger.error("Erro genérico: %s", str(e))
    return render_template('error.html', error="Ocorreu um erro inesperado."), 500

# Rota principal
@app.route('/')
def index():
    if 'suap_token' in session:
        try:
            user = User(oauth)
            user_data = user.get_user_dados()
            logger.debug("Dados do usuário obtidos: %s", user_data.json())
            return render_template('user.html', user_data=user_data.json())
        except Exception as e:
            logger.error("Erro ao obter dados do usuário: %s", str(e))
            return render_template('error.html', error="Erro ao carregar os dados do usuário.")
    return render_template('index.html')

# Rota para boletim
@app.route("/boletim", methods=["GET"])
def boletim():
    if 'suap_token' not in session:
        return redirect(url_for('login'))

    try:
        user = User(oauth)
        user_data = user.get_user_dados()
        anos_letivos = user.get_user_anos_letivos()

        data = {
            "user_data": user_data.json(),
            "anos_letivos": anos_letivos.json(),
        }

        # Verifica se o usuário selecionou um ano/semestre
        ano_letivo = request.args.get('ano_letivo')
        if ano_letivo:
            ano, periodo = ano_letivo.split(".")
            boletim = user.get_user_boletim(ano, periodo)
            data["boletim"] = boletim.json()
            data["ano_selecionado"] = ano_letivo

        return render_template("boletim.html", data=data)
    except Exception as e:
        logger.error("Erro ao carregar boletim: %s", str(e))
        return render_template('error.html', error="Erro ao carregar o boletim.")

# Rota para login
@app.route('/login')
def login():
    try:
        redirect_uri = url_for('auth', _external=True)
        return oauth.suap.authorize_redirect(redirect_uri)
    except Exception as e:
        logger.error("Erro durante o login: %s", str(e))
        return render_template('error.html', error="Erro durante o processo de login.")

# Rota para logout
@app.route('/logout')
def logout():
    session.pop('suap_token', None)
    return redirect(url_for('index'))

# Rota para autorização do login
@app.route('/login/authorized')
def auth():
    try:
        token = oauth.suap.authorize_access_token()
        session['suap_token'] = token
        logger.debug("Token de sessão recebido: %s", token)
        return redirect(url_for('index'))
    except Exception as e:
        logger.error("Erro ao autorizar o login: %s", str(e))
        return render_template('error.html', error="Erro ao processar a autorização de login.")

if __name__ == "__main__":
    app.run(debug=True)

# Exibir CLIENT_ID no log para depuração (remova isso em produção!)
logger.debug("CLIENT_ID: %s", CLIENT_ID)

from flask import Flask, redirect, url_for, session, request, render_template
from authlib.integrations.flask_client import OAuth
from main import oauthRegister, User
import jinja2
from dotenv import load_dotenv
import os

# Carregar as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)
app.debug = True
app.secret_key = os.getenv('SECRET_KEY', 'development')  # Mude para uma chave secreta real em produção
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
    return render_template('500.html', error=str(e)), 500

@app.route('/')
def index():
    if 'suap_token' in session:
        user = User(oauth)
        user_data = user.get_user_dados()
        print(user_data.json())  # Isso pode ser removido ou logado em produção
        data = {"user_data": user_data.json()}
        return render_template('user.html', data=data)
    else:
        return render_template('index.html')

@app.route("/boletim", methods=["GET"])
def boletim():
    if 'suap_token' not in session:
        return redirect(url_for('login'))  # Garantir que o usuário esteja logado

    user = User(oauth)
    user_data = user.get_user_dados()
    anos_letivos = user.get_user_anos_letivos()
    data = {
        "user_data": user_data.json(),
        "anos_letivos": anos_letivos.json(),
    }

    # Verifica se o usuário selecionou um ano/semestre
    if request.args.get('ano_letivo'):
        try:
            ano_letivo, periodo_letivo = str(request.args.get('ano_letivo')).split(".")
            boletim = user.get_user_boletim(ano_letivo, periodo_letivo)
            data["boletim"] = boletim.json()
            data["ano_selecionado"] = str(request.args.get('ano_letivo'))

        except jinja2.exceptions.UndefinedError as e:
            handle_jinja2_error(e)
    return render_template("boletim.html", data=data)

@app.route('/login')
def login():
    """Redireciona o usuário para o fluxo de autorização do SUAP."""
    redirect_uri = url_for('auth', _external=True)
    return oauth.suap.authorize_redirect(redirect_uri)

@app.route('/logout')
def logout():
    """Realiza o logout e remove o token de sessão."""
    session.pop('suap_token', None)
    return redirect(url_for('index'))

@app.route('/login/authorized')
def auth():
    """Recebe o token após autorização e o salva na sessão."""
    token = oauth.suap.authorize_access_token()
    session['suap_token'] = token
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)

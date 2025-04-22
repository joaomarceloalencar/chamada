import os
from flask import Flask, render_template, request, redirect, url_for, session
from google.oauth2 import id_token
from google.auth.transport import requests

APPLICATION_ROOT = os.getenv('APPLICATION_ROOT', '')
print(f"APPLICATION_ROOT está definido como: '{APPLICATION_ROOT}'")


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'sua_chave_secreta_padrao_para_dev')

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
ALLOWED_DOMAINS = ['alu.ufc.br', 'ufc.br']

@app.route('/')
def index():
    """Rota principal que exibe a tela de login."""
    base_url = os.environ.get('BASE_URL', 'http://localhost:5001')
    return render_template('login.html', GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID, BASE_URL=base_url)

@app.route('/login/google', methods=['POST'])
def google_login():
    """Rota para receber o token de identificação do Google."""
    credential = request.form.get('credential')
    if credential:
        try:
            idinfo = id_token.verify_oauth2_token(credential, requests.Request(), GOOGLE_CLIENT_ID)

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            if 'hd' in idinfo and idinfo['hd'] in ALLOWED_DOMAINS:
                user_id = idinfo['sub']
                email = idinfo['email']
                name = idinfo.get('name')  # Recupera o nome do idinfo
                session['user_email'] = email
                session['user_name'] = name    # Armazena o nome na sessão
                print(f"Email armazenado na sessão: {session.get('user_email')}")
                print(f"Nome armazenado na sessão: {session.get('user_name')}")
                return redirect(url_for('profile'))
            else:
                return "Login não permitido para este domínio.", 403

        except ValueError:
            # Token inválido
            return "Falha na autenticação.", 401
    else:
        return "Token de identificação não encontrado.", 400

@app.route('/profile')
def profile():
    """Rota para exibir o perfil do usuário após o login."""
    if 'user_email' in session:
        user_email = session['user_email']
        user_name = session.get('user_name')
        return render_template('profile.html', user_email=user_email, user_name=user_name)
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Rota para deslogar o usuário."""
    session.pop('user_email', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
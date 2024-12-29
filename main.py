import os
from authlib.integrations.flask_client import OAuth
from flask import session
from decouple import config

def oauthRegister(oauth, **kwargs):
    return oauth.register(
        name=kwargs["name"],
        client_id=config("CLIENT_ID"),
        client_secret=config("CLIENT_SECRET"),
        api_base_url=kwargs["api_base_url"],
        request_token_url=kwargs["request_token_url"],
        access_token_method=kwargs["access_token_method"],
        access_token_url=kwargs["access_token_url"],
        authorize_url=kwargs["authorize_url"],
        fetch_token=lambda: session.get('suap_token')
    )

class User:
    def __init__(self, oauth):
        self.oauth = oauth
        
    def get_user_dados(self):
        return self.oauth.suap.get('v2/minhas-informacoes/meus-dados')

    def get_user_boletim(self, ano_letivo, periodo_letivo):
        return self.oauth.suap.get(f"/api/v2/minhas-informacoes/boletim/{ano_letivo}/{periodo_letivo}/")
    
    def get_user_anos_letivos(self):
        return self.oauth.suap.get(f"/api/v2/minhas-informacoes/meus-periodos-letivos/")

from dataclasses import dataclass
from flask import Blueprint,redirect,url_for,session,current_app
from authlib.integrations.flask_client import OAuth
from config import GOOGLE_CLIENT_ID,GOOGLE_CLIENT_SECRET,DEV_LOGIN


@dataclass(frozen=True)
class Identity:
  issuer:str
  subject:str
  email:str|None
  name:str|None
  picture:str|None

oauth=OAuth()
bp=Blueprint('auth',__name__,url_prefix='/auth')

def init_oauth(app):
 oauth.init_app(app)
 if GOOGLE_CLIENT_ID:
  oauth.register(name='google',
                 client_id=GOOGLE_CLIENT_ID,
                 client_secret=GOOGLE_CLIENT_SECRET,
                 server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
                 client_kwargs={'scope':'openid email profile'})

@bp.get('/login')
def login():
 if not GOOGLE_CLIENT_ID and DEV_LOGIN:
  return redirect(url_for('auth.dev_login'))
 return oauth.google.authorize_redirect(url_for('auth.callback',
                                                _external=True))

@bp.get('/callback')
def callback():
 token=oauth.google.authorize_access_token()
 info=token.get('userinfo') or oauth.google.userinfo()
 session['identity']={'issuer':info.get('iss','https://accounts.google.com'),
                      'subject':info['sub'],'email':info.get('email'),
                      'name':info.get('name'),'picture':info.get('picture')}
 return redirect(url_for('main.index'))

@bp.get('/dev-login')
def dev_login():
 if not DEV_LOGIN:
  return ('Disabled',403)
 session['identity']={'issuer':'dev',
                      'subject':'local-demo-user',
                      'email':'demo@example.com',
                      'name':'Demo Learner',
                      'picture':None}
 return redirect(url_for('main.index'))

@bp.get('/logout')
def logout():
  session.clear()
  return redirect(url_for('main.index'))

def identity_from_session():
 x=session.get('identity')
 return Identity(**x) if x else None

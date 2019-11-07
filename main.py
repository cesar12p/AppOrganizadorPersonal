import webapp2
#3 metodo
import os
import jinja2
import random
import logging
from google.appengine.ext import ndb
from webapp2_extras import sessions
from Crypto.Hash import SHA256
userg=""
resp = ""
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)
template_values={}
class Objeto_Usuario(ndb.Model):
    username = ndb.StringProperty()
    password = ndb.StringProperty()
    ganadas = ndb.IntegerProperty()
    perdidas = ndb.IntegerProperty()

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def render(self, template, **kw):
		self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

class MainPage(Handler):
    def get(self):
        fondo="bg-info"
        msg=""
        self.render("index.html",fondo=fondo, msg=msg)
    def post(self):
        global template_values
        user = self.request.get('user')
        pw = self.request.get('contra')
        pw=SHA256.new(pw).hexdigest()
        logging.info('Checking user='+ str(user) + 'pw='+ str(pw))
        msg = ''
        fondo="bg-warning"
        if pw == '' or user == '':
            msg = "Error Ingresa tu usuario y password"
            self.render("index.html", msg=msg ,fondo=fondo)
        else:
            consulta=Objeto_Usuario.query(ndb.AND(Objeto_Usuario.username==user, Objeto_Usuario.password==pw )).get()
            if consulta is not None:
                logging.info('POST consulta=' + str(consulta))
                #Vinculo el usuario obtenido de mi datastore con mi sesion.
                self.session['user'] = consulta.username
                self.session['ganadas']=consulta.ganadas
                self.session['perdidas']=consulta.perdidas
                logging.info("%s just logged in" % user)
                global userg
                userg=user
                template_values={
                    'user':self.session['user'],
                    'ganadas':self.session['ganadas'],
                    'perdidas':self.session['perdidas']
                }
                self.render("Bienvenido.html", user=template_values)
            else:
                logging.info('POST consulta=' + str(consulta))
                fondo="bg-danger"
                msg = 'El usuario o el password son Incorectos  Intenta de nuevo'
                self.render("index.html", msg=msg, fondo=fondo)

class Registrar(Handler):
    def get(self):
        self.render("Registro.html")

    def post(self):
        user = self.request.get('user')
        pw = self.request.get('contra')
        pw=SHA256.new(pw).hexdigest()
        cuenta = Objeto_Usuario(username=user, password = pw, ganadas=0, perdidas=0)
        cuentakey = cuenta.put()
        cuenta_user=cuentakey.get()
        if cuenta_user == cuenta:
            msg = "Registrado"
            self.render("index.html", msg=msg)
class Salir(Handler):
    def get(self):
        if self.session.get('user'):
            logging.info("%s bye")
            msg ="Cerraste sesion"
            fondo="bg-secondary"
            self.render("index.html", error=msg ,fondo=fondo)
            del self.session['user']

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'some-secret-key',
}

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/click_login', MainPage),
                               ('/registrame',Registrar),
                               ('/salir',Salir)
                               ], debug=True, config=config)

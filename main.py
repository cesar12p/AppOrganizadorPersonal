import webapp2
#3 metodo
import os
import jinja2
import random
import logging
from google.appengine.ext import ndb
from webapp2_extras import sessions
from Crypto.Hash import SHA256
user=""
userg=""
resp = ""
consulta=""
lista = []
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)
template_values={}
nota_values={}
class Objeto_Nota(ndb.Model):
    Titulo = ndb.StringProperty()
    Descripcion = ndb.StringProperty()
class Objeto_Usuario(ndb.Model):
    username = ndb.StringProperty()
    password = ndb.StringProperty()
    email=ndb.StringProperty()
    nota=ndb.StructuredProperty(Objeto_Nota, repeated=True)
 

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
        global consulta
        global user
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
                logging.info("%s just logged in" % user)
                template_values={
                    'user':self.session['user']
                }
                self.render("Bienvenido.html", user=template_values)
            else:
                logging.info('POST consulta=' + str(consulta))
                fondo="bg-danger"
                msg = 'El usuario o el password son Incorectos  Intenta de nuevo'
                self.render("index.html", msg=msg, fondo=fondo)
class Menu (Handler):
    def get(self):
        global template_values
        self.render("Bienvenido.html",user=template_values)


class Registrar(Handler):
    def get(self):
        self.render("Registro.html")
    def post(self):
        user = self.request.get('user')
        pw = self.request.get('contra')
        pw=SHA256.new(pw).hexdigest()
        cuenta = Objeto_Usuario(username=user, password = pw)
        cuentakey = cuenta.put()
        cuenta_user=cuentakey.get()
        if cuenta_user == cuenta:
            msg = "Registrado"
            self.render("index.html", msg=msg)
class Nota(Handler):
    def post(self):
        global consulta
        global lista
        Titulo = self.request.get('Titulo')
        Descripcion = self.request.get('Descripcion')
        newNota=Objeto_Nota(Titulo=Titulo,Descripcion=Descripcion)
        consulta.nota.append(newNota)
        consulta.put()
        lista = []
        for i in consulta.nota:
            lista.append(i) 
        self.render("Mostrar.html", lista=lista)

class Salir(Handler):
    def get(self):
        if self.session.get('user'):
            logging.info("%s bye")
            msg ="Cerraste sesion"
            fondo="bg-secondary"
            self.render("index.html", error=msg ,fondo=fondo)
            del self.session['user']
class Editar(Handler):
    def post(self):
        IdTitulo = self.request.get('idTitulo')
        EditTitulo=self.request.get('EditTitulo')
        EditDescrip=self.request.get('EditDescripcion')
        cont=0
        for i in lista:
            if i.Titulo==IdTitulo:
                consulta.nota[cont].Titulo=EditTitulo
                consulta.nota[cont].Descripcion=EditDescrip
                consulta.put()
            cont+=1
        global template_values
        global lista
        self.render("Mostrar.html",lista=lista)
            
        
        
        ##consulta.nota.Titulo.put()

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'some-secret-key',
}

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/click_login', MainPage),
                               ('/registrame',Registrar),
                               ('/AddNota',Nota),
                               ('/salir',Salir),
                               ('/editar',Editar),
                               ('/menu',Menu)
                               ], debug=True, config=config)

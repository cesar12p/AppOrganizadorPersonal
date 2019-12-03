import webapp2
#3 metodo
import os
import jinja2
import random
import logging
import datetime
from google.appengine.ext import ndb
from webapp2_extras import sessions
from Crypto.Hash import SHA256
user=""
userg=""
resp = ""
consulta=""
listNotas = []
listContac = []
listEvent =[]
lista = []
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)
template_values={}
nota_values={}
class Objeto_Nota(ndb.Model):
    Titulo = ndb.StringProperty()
    Descripcion = ndb.TextProperty()
class Objeto_Contacto(ndb.Model):
    Nombre = ndb.StringProperty()
    Telefono = ndb.IntegerProperty()
    FechaNaci = ndb.StringProperty()
    Correo = ndb.StringProperty()
class Objeto_Evento(ndb.Model):
    Titulo = ndb.StringProperty()
    Descripcion = ndb.TextProperty()
    Fecha = ndb.StringProperty()

class Objeto_Usuario(ndb.Model):
    username = ndb.StringProperty()
    password = ndb.StringProperty()
    email=ndb.StringProperty()
    nota=ndb.StructuredProperty(Objeto_Nota, repeated=True)
    evento=ndb.StructuredProperty(Objeto_Evento, repeated=True)
    contacto=ndb.StructuredProperty(Objeto_Contacto, repeated=True)
 

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
                ListaContacto()
                ListaNotas()
                ListaEvento()
                listEvent.sort()
                self.render("Bienvenido.html", user=template_values,listContac=listContac,listNotas=listNotas,listEvent=listEvent)
            else:
                logging.info('POST consulta=' + str(consulta))
                fondo="bg-danger"
                msg = 'El usuario o el password son Incorectos  Intenta de nuevo'
                self.render("index.html", msg=msg, fondo=fondo)
class Menu (Handler):
    def get(self):
        global template_values
        ListaContacto()
        ListaNotas()
        ListaEvento()
        listEvent.sort('Fecha')
        self.render("Bienvenido.html", user=template_values,listContac=listContac,listNotas=listNotas,listEvent=listEvent)
        


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

class AddNota(Handler):
    global template_values
    def get(self):
        self.render("AddNota.html",user=template_values)
    def post(self):
        global consulta
        Titulo = self.request.get('Titulo')
        Descripcion = self.request.get('Descripcion')
        newNota=Objeto_Nota(Titulo=Titulo,Descripcion=Descripcion)
        consulta.nota.append(newNota)
        consulta.put()
        ListaNotas() 
        self.render("ShowNota.html",user=template_values,list=listNotas)
class AddContacto(Handler):
    global template_values
    def get(self):
        self.render("AddContacto.html",user=template_values)
    def post(self):
        global consulta
        Nombre = self.request.get('Nombre')
        Telefono = self.request.get('Telefono')
        Fecha = self.request.get('Fecha')
        Correo = self.request.get('Correo')
        newContac=Objeto_Contacto(Nombre=Nombre,Telefono=int(Telefono),FechaNaci=Fecha,Correo=Correo)
        consulta.contacto.append(newContac)
        consulta.put()
        ListaContacto()
        self.render("ShowContacto.html",user=template_values,list=listContac)
class AddEvento(Handler):
    global template_values
    def get(self):
        self.render("AddEvento.html",user=template_values)
    def post(self):
        global consulta
        Titulo = self.request.get('Titulo')
        Descripcion = self.request.get('Descripcion')
        Fecha = self.request.get('Fecha')
        newEvent=Objeto_Evento(Titulo=Titulo,Descripcion=Descripcion,Fecha=Fecha)
        consulta.evento.append(newEvent)
        consulta.put()
        ListaEvento()
        self.render("ShowEvento.html",user=template_values,list=listEvent )

class ShowNota(Handler):
    def get(self):
        ListaNotas() 
        self.render("ShowNota.html",user=template_values,list=listNotas)
    def post(self):
        Titulo = self.request.get('Titulo')
        Descripcion= self.request.get('Descripcion')

        self.render("EditNota.html",Titulo=Titulo,Descripcion=Descripcion)
def ListaNotas():
    global listNotas
    listNotas = []
    for i in consulta.nota:
        listNotas.append(i) 
class ShowEvento(Handler):
    def get(self):
        ListaEvento()
        self.render("ShowEvento.html",user=template_values,list=listEvent)
    def post(self):
        Titulo = self.request.get('Titulo')
        Descripcion= self.request.get('Descripcion')
        Fecha = self.request.get('Fecha')
        self.render("EditEvento.html",Titulo=Titulo,Descripcion=Descripcion, Fecha=Fecha)
def ListaEvento():
    global listEvent
    listEvent = []
    for i in consulta.evento:
        listEvent.append(i) 

class ShowContact(Handler):
    def get(self):
        Id=self.request.get('Id')
        ListaContacto()
        logging.info("MENSAJE: "+Id)
        self.render("ShowContacto.html",user=template_values,list=listContac)
    def post(self):
        Nombre = self.request.get('Nombre')
        Telefono = self.request.get('Telefono')
        Fecha= self.request.get('Fecha')
        Correo=self.request.get('Correo')
        self.render("EditContacto.html",user=template_values,Nombre=Nombre,Telefono=Telefono,Fecha=Fecha,Correo=Correo)
def ListaContacto():
    global listContac
    listContac = []
    for i in consulta.contacto:
        listContac.append(i)
class EditNota(Handler):
    def get(self):
        global consulta
        IdTitulo = self.request.get('IdTitulo')
        cont=0
        for i in listNotas:
            if i.Titulo==IdTitulo:
                consulta.nota.pop(cont)
                consulta.put()
                break
            cont+=1
        ListaNotas()
        self.render("ShowNota.html",user=template_values,list=listNotas)
    def post(self):
        global consulta
        IdTitulo = self.request.get('IdTitulo')
        EditTitulo=self.request.get('EditTitulo')
        EditDescrip=self.request.get('EditDescripcion')
        logging.info('ENTRO AL EDITAR')
        cont=0
        for i in listNotas:
            if i.Titulo==IdTitulo:
                consulta.nota[cont].Titulo=EditTitulo
                consulta.nota[cont].Descripcion=EditDescrip
                consulta.put()
                break
            cont+=1
        ListaNotas()
        self.render("ShowNota.html",user=template_values,list=listNotas)
class EditarEvento(Handler):
    def get(self):
        global consulta
        IdTitulo = self.request.get('IdTitulo')
        cont=0
        for i in listEvent:
            if i.Titulo==IdTitulo :
                consulta.evento.pop(cont)
                consulta.put()
                break
            cont+=1
        ListaEvento()
        self.render("ShowEvento.html",user=template_values,list=listEvent)
    def post(self):
        global consulta
        IdTitulo= self.request.get('IdTitulo')
        EditTitulo=self.request.get('EditTitulo')
        EditDescrip=self.request.get('EditDescripcion')
        EditFecha=self.request.get('EditFecha')
        cont=0
        for i in listEvent:
            if i.Titulo==IdTitulo:
                consulta.evento[cont].Titulo=EditTitulo
                consulta.evento[cont].Descripcion=EditDescrip
                consulta.evento[cont].Fecha=EditFecha
                consulta.put()
                break
            cont+=1
        ListaEvento()
        self.render("ShowEvento.html",user=template_values,list=listEvent)
class EditarContacto(Handler):
    def get(self):
        global consulta
        IdNombre = self.request.get('IdNombre')
        cont = 0
        for i in listContac:
            if i.Nombre==IdNombre:
                consulta.contacto.pop(cont)
                consulta.put()
                break
            cont+=1
        ListaContacto()
        self.render("ShowContacto.html",user=template_values,list=listContac)
    def post(self):
        global consulta
        IdNombre=self.request.get('IdNombre')
        EditNombre=self.request.get('EditNombre')
        EditTelefono=self.request.get('EditTelefono')
        EditFecha=self.request.get('EditFecha')
        EditCorreo=self.request.get('EditCorreo')
        cont=0
        for i in listContac:
            if i.Nombre==IdNombre:
                consulta.contacto[cont].Nombre=EditNombre
                consulta.contacto[cont].Telefono=int(EditTelefono)
                consulta.contacto[cont].FechaNaci=EditFecha
                consulta.contacto[cont].Correo=EditCorreo
                consulta.put()
                break
            cont+=1
        ListaContacto()
        self.render("ShowContacto.html",user=template_values,list=listContac)
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
                               ('/addEvent',AddEvento),
                               ('/addNota',AddNota),
                               ('/addContact',AddContacto),
                               ('/AddNota',Nota),
                               ('/showNota',ShowNota),
                               ('/showEvent',ShowEvento),
                               ('/showContact',ShowContact),
                               ('/editNota',EditNota),
                               ('/editEvent',EditarEvento),
                               ('/editContact',EditarContacto),
                               ('/salir',Salir),
                               ('/editar',Editar),
                               ('/menu',Menu)
                               ], debug=True, config=config)

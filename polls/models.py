from __future__ import unicode_literals
import requests
import simplejson
from django.db import models
from polls import settings
from bs4 import BeautifulSoup
import nltk


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class FanPage(models.Model):
    page_id = models.CharField(max_length=100)


class Post(models.Model):
    post_id = models.CharField(max_length=200)
    message = models.TextField()
    fanpage = models.ForeignKey(FanPage)


class Comment(models.Model):
    message = models.TextField()
    date = models.CharField(max_length=50)
    user_name = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)
    post = models.ForeignKey(Post)


# definicion de las funciones

def get_access_token():
    # pedir access token
    # este primero client id es mi id para usar la api
    url_access_token = 'https://graph.facebook.com/oauth/access_token?%20client_id={}&client_secret={}&grant_type=client_credentials'.format(settings.CLIENT_ID, settings.CLIENT_SECRET)
    response = requests.get(url_access_token)
    access_token = simplejson.loads(response.text)['access_token']
    return access_token


def get_posts_from_fanpage(page_id, access_token, next_url=None):
    # resonse.text  es un string el contenido de la repuesta... loads lo hace diccionario y de ahi los corchetes obtengo la clave accesos token
    # pedir el feed (muro) de posts de la pagina

    if next_url is None:
        url_feed = 'https://graph.facebook.com/v2.8/{}/feed?access_token={}'.format(page_id, access_token)
    else:
        url_feed = next_url

    response = requests.get(url_feed)

    # el request es lo que llama la info con la url feed que incorpora esos dos argumentos
    json = simplejson.loads(response.text)  # loads convierte el string de JSON a un diccionario de Python
    #post4_id = json['data'][3]['id']
    return json


def get_comments_from_post(post_id, access_token):
    # pedir los comments del post
    # https://graph.facebook.com/v2.8/121305961374091_688955347942480/comments?access_token=234693623606637|g37OnFOwJcnckcSvkayhfImOlTM
    url_comments = 'https://graph.facebook.com/v2.8/{}/comments?access_token={}'.format(post_id, access_token)
    response = requests.get(url_comments)
    json = simplejson.loads(response.text)
    return json


def save_comments(post, comments):
    for comment_data in comments['data']:
        comment = Comment() # llama la constructor, se crea el objeto
        comment.message = comment_data['message']
        comment.date = comment_data['created_time']

        try:
            comment.user_name = comment_data['from']['name']
            comment.user_id = comment_data['from']['id']
        except KeyError:
            comment.user_name = 'Unknown'
            comment.user_id = 'Unknown'

        comment.post = post # asocio el post al comentario a crear
        comment.save() # se persiste el objeto y sus valores en la base de datos


def save_and_print_posts(page_id, posts, access_token):
    try:
        fanpage = FanPage.objects.get(page_id=page_id)
    except Exception:
        fanpage = FanPage()
        fanpage.page_id = page_id
        fanpage.save()
    try:
        for post in posts['data']:
            #print(repr(post['message']))

            post_id = post['id']
            comments = get_comments_from_post(post_id, access_token)

            #for comment in comments['data']:
            #    print(' - ' + comment['message'])

            post_object = Post()
            post_object.post_id = post_id
            post_object.message = post['message']
            post_object.fanpage = fanpage
            post_object.save()

            save_comments(post_object, comments)
    except Exception:
        pass


class Website(models.Model):
    url = models.URLField()

    def __str__(self):
        return self.url


class Oracion(models.Model):
    texto = models.CharField(max_length=500)
    website = models.ForeignKey(Website)

    def __str__(self):
        return self.texto


class Palabra(models.Model):
    texto = models.CharField(max_length=50)
    ocurrencias = models.PositiveIntegerField(default=0)
    oracion = models.ForeignKey(Oracion)

    def __str__(self):
        return self.texto


class ExtractorPalabras():
    def limpiar_palabra(self, texto, caracter):
        return texto.split(caracter)[0]

    def extraer(self, url):
        todas_oraciones = list()  # todas las oraciones en la URL

        spanish_stops = set(nltk.corpus.stopwords.words('spanish'))
        spanish_stops.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}'])

        # Se pide el HTML de la URL
        response = requests.get(url)
        # aca me tira html crudo texto plano
        html = response.text
        # beautifulsopu te lo ordena como los arbol los a ,, lo p
        soup = BeautifulSoup(html, 'html.parser')

        # Se obtienen uno por uno los parrafos en el HTML
        for p in soup.find_all('p'):
            contenido = p.text
            if contenido != "":
                oraciones = nltk.sent_tokenize(contenido)  # las oraciones en el parrafo actual
                todas_oraciones.extend(oraciones)

        # Se crean los modelos
        objeto_website = Website()
        objeto_website.url = url
        objeto_website.save()

        for texto_oracion in todas_oraciones:
            objeto_oracion = Oracion()
            objeto_oracion.texto = texto_oracion
            objeto_oracion.website = objeto_website
            objeto_oracion.save()

            # Se obtiene una lista de los textos de cada palabra en la oracion
            texto_palabras = nltk.tokenize.regexp_tokenize(texto_oracion, '\s+', gaps=True)

            # Se eliminan las stops words
            texto_palabras_limpio = []
            for texto_palabra in texto_palabras:
                if texto_palabra.lower() not in spanish_stops:
                    # Limpiar signos de puntuacion en el texto de la palabra
                    texto_palabra = self.limpiar_palabra(texto_palabra, '[')
                    texto_palabra = self.limpiar_palabra(texto_palabra, ',')
                    texto_palabra = self.limpiar_palabra(texto_palabra, '{')
                    texto_palabra = self.limpiar_palabra(texto_palabra, '(')
                    texto_palabra = self.limpiar_palabra(texto_palabra, ')')
                    texto_palabra = self.limpiar_palabra(texto_palabra, '.')
                    texto_palabra = self.limpiar_palabra(texto_palabra, ';')
                    texto_palabra = self.limpiar_palabra(texto_palabra, ':')

                    if len(texto_palabra) > 0:
                        texto_palabras_limpio.append(texto_palabra.lower().replace('.', ''))

            for texto_palabra in texto_palabras_limpio:
                try:
                    palabra = Palabra.objects.get(texto=texto_palabra, oracion=objeto_oracion)
                    palabra.ocurrencias += 1
                except Exception:
                    palabra = Palabra()
                    palabra.texto = texto_palabra
                    palabra.oracion = objeto_oracion
                    palabra.ocurrencias = 1

                palabra.save()

        return objeto_website

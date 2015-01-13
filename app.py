# -*- coding: utf-8 -*-
import tweepy
import web
from web import form
from tweepy.streaming import StreamListener
import json
from time import sleep
from sys import exit
from pymongo import MongoClient
import geocoder

# #Conexión a db donde están los tweets guardados
client = MongoClient('localhost', 27017)
db = client['DAI-Graficos']
tweetCol = db.tweetsDefensa

# Consumer keys and access tokens, used for OAuth
consumer_key = 'qf7iB47OFNdZkRRwt7qane7oS'
consumer_secret = 'n4Jtfj5r0ahzX2SEfJo5sbOUms5EZ9WLsSBVce7NZkwvE1Kf5C'
access_token = '170029150-7YulbF4L42szrGg9sKfxiebZV2GJsBx6Aijiu8uU'
access_token_secret = 'w44PH8x2MbZCPm8kuscH53g2AGwngmI6yiCQfx75qBDMw'

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Creation of the actual interface, using authentication
api = tweepy.API(auth)

#----------FUNCIONES DE BUSQUEDA DE TWEETS----------
def buscarTweets(contenido, direccion, radio):
	insertados = 0;
	if(geocoder.google(direccion).lat > 0.0):
		location = geocoder.google(direccion)
		geocode = str(location.lat) + "," + str(location.lng) + "," + str(radio) + "km"
		result = api.search(q=str(contenido), geocode=geocode, rpp=1000, show_user=1)
		
		for tweet in result:
			userCity = str(tweet.user.time_zone)
			if (tweet.coordinates != None):
				tweetCoordinates = tweet.coordinates['coordinates']
				g = geocoder.bing(tweetCoordinates, method='reverse')
				tweetLocation = g.locality if (g.locality != None) else g.country
			else:
				tweetCoordinates = None
				tweetLocation = None
				
			if (geocoder.google(tweet.user.location).locality):
				userCity = geocoder.google(tweet.user.location).locality
			else: 
				if (geocoder.google(tweet.user.location).country) :
					userCity = geocoder.google(tweet.user.location).country
						
			tweetNuevo = {
				'contenido' : contenido,
				'direccion' : direccion,
				'radio': radio,
 				'texto': tweet.text,
 			 	'ciudadUsuario': str(userCity),
 			 	'coordenadasCiudadUsuario': [geocoder.google(tweet.user.location).lat, geocoder.google(tweet.user.location).lng],
 			 	'CoordenadasTweet':tweetCoordinates,
 			 	'ciudadTweet':tweetLocation,
 			 	'nombreUsuario':tweet.user.screen_name
 			}
			
			print tweetNuevo
			insertados += 1
			tweetCol.insert(tweetNuevo)
		print 'FIN'
	return insertados

def hacerConteo(contenido,ajax = 0):
	ciudades = tweetCol.distinct("ciudadUsuario")
	conteo = []
	for c in ciudades:
		numero = tweetCol.find({"ciudadUsuario":c,"contenido" : contenido}).count()
		if(numero > 0 and c != 'None'):
			if(ajax > 0):
				conteo={}
				conteo[c]=numero;
			else:
				conteo.append([c,numero])
	return conteo

#----------FIN FUNCIONES DE BUSQUEDA DE TWEETS----------


myform = form.Form(
	form.Textbox('contenido',
				description='Contenido del tweet',
				class_='form-control'),
	form.Textbox('direccion',
				description='Dirección a la que queremos ver tweets cercanos',
				 class_='form-control'),
	form.Textbox('radio',
				description='Radio de busqueda en km',
				 class_='form-control')
				)


render = web.template.render('templates/')
urls = ('/', 'index',
		'/ajax', 'ajax')

app = web.application(urls, globals())

class index:
	
	def GET(self):
		form = myform()
		return render.app(form,direccion="",tweets = {},series =[])
	
	def POST(self):
		form = myform()
		form.validates()
		
		contenido = str(form["contenido"].value);
		direccion = str(form["direccion"].value);
		radio =  str(form["radio"].value);
		centro = str(geocoder.google(direccion).lat) + "," + str(geocoder.google(direccion).lng)
		buscarTweets(contenido, direccion, radio)
		tweetsDB = tweetCol.find({"contenido" : contenido, "direccion" : direccion,"radio" : radio} )
		tweets = []
		for t in tweetsDB:
			tweets.append(t)
			
		series = hacerConteo(contenido);
		return render.app(form,centro,tweets,series)

class ajax:
	def GET(self ):
		variables = web.input('contenido')
		series = hacerConteo(variables.contenido)
		print series
		seriesJSON = json.dumps(series)
		print seriesJSON
		return seriesJSON

	
if __name__ == "__main__":
	web.internalerror = web.debugerror
	app.run()

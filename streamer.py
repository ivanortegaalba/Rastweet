# -*- coding: utf-8 -*-
import tweepy
import web
from web import form
from tweepy.streaming import StreamListener
import json
from time import sleep
from sys import exit

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


"""Lo primero que deberemos hacer es crear una clase heredada de tweepy.
StreamListener. Esta será, como bien indica la superclase, la que escuche el flujo de tweets"""

class StreamListener(tweepy.StreamListener):
	'''Cuando un Tweet haga match con nuestros targetTerms será pasado a
	esta función'''
	def on_data(self, data):
		# Asignamos el JSON de los datos a la variable data
		data = json.loads(data)
		# Intentamos ejecutar el codigo
		try:
			# Si los datos no contienen cooedenadas no nos interesan
			if data['geo'] is not None:
				'''recuperamos los elementos que nos interesan de data
				y los imprimimos por pantalla'''
				print( data['user']['name'].encode('ascii', 'ignore'))
				print( data['user']['screen_name'].encode('ascii', 'ignore') )
				print( data['geo']['coordinates'])
				
			return True
		# En caso de un error lo imprimimos
		except Exception, e:
			print('[!] Error: {0}'.format(e))
			
	# Si alcanzamos el limite de llamadas alerta y espera 10"
	def on_limit(self, track):
		print('[!] Limit: {0}').format(track)
		sleep(10)
	
	
	# En caso de producirse un error interrumpe el listener
	# https://dev.twitter.com/overview/api/response-codes
	def on_error(self, status):
		print('[!] Error: {0}').format(status)
		return False


def streamAPI(auth):
	# Instanciamos nuestro listener
	l = StreamListener()
	# Iniciamos el streamer con el objeto OAuth y el listener
	streamer = tweepy.Stream(auth=auth, listener=l)
	# Definimos los terminos de los que queremos hacer un tracking
	targetTerms = ['hola', 'buenos dias', 'buenas tardes', 'buenas noches']
	# Iniciamos el streamer, pasandole nuestros trackTerms
	streamer.filter(track=targetTerms,locations=[-3.633835,37.149428,-3.550571,37.212465])
	
print('\n[*] Iniciando streamer:')
streamAPI(auth)

render = web.template.render('templates/')

urls = ('/', 'index')
app = web.application(urls, globals())

class index:
	
	def GET(self):
			
		return render.tweets()

if __name__ == "__main__":
	web.internalerror = web.debugerror
	app.run()

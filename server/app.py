from wsgiref.handlers import format_date_time
import config
import json
import logging
import rpc
import time
import utils
import webapp2

class ContentRequestHandler(webapp2.RequestHandler):
	def get(self, outputFormat, key):
		if not key:
			self.error(404)
			self.response.out.write('404 Not Found')
			return

		doc = utils.getContentObj(key)
		if not doc:
			self.error(404)
			self.response.out.write('404 Not Found')
			return

		maxAge = config.contentCacheDuration + doc['timestamp'] - int(time.time())
		if maxAge <= 0:
			logging.error("Invalid values -- maxAge: %d, cacheDuration: %d, cacheTimestamp: %d, time: %d ", maxAge, config.contentCacheDuration, doc['timestamp'], int(time.time()))

		self.response.headers["Cache-Control"] = "public, max-age=%d" % maxAge
		self.response.headers["Expires"] = format_date_time(time.time() + maxAge)
		
		if outputFormat.lower() == 'json':
			self.response.headers["Content-Type"] = "application/json"
			
			callback = self.request.get('callback');
			if callback and callback.isalnum():
				self.response.out.write("%s(%s)" % (callback, json.dumps(doc)))
			else:
				self.response.out.write(json.dumps(doc))
		else:
			self.response.out.write(doc['content'])

class RpcRequestHandler(webapp2.RequestHandler):

	def get(self, action):
		if not action or action[0] == '_':
			self.error(404)
			self.response.out.write('404 Not Found')
			return

		func = getattr(rpc.RpcMethods(), action, None)
		if not func:
			self.error(404)
			self.response.out.write('404 Not Found')
			return

		logging.info("Received RPC GET: %s()", action)
		result = func()
		self.response.out.write(json.dumps(result))

	def post(self, action):
		if not action or action[0] == '_':
			self.error(404)
			self.response.out.write('404 Not Found')
			return

		func = getattr(rpc.RpcMethods(), action, None)
		if not func:
			self.error(404)
			self.response.out.write('404 Not Found')
			return

		logging.info("Received RPC POST: %s(%s)", action, self.request.body)
		argObj = json.loads(self.request.body)
		result = func(argObj)
		self.response.out.write(json.dumps(result))

app = webapp2.WSGIApplication([
	('/rpc/(.*)', RpcRequestHandler),
	('/(.*)/(.*)', ContentRequestHandler),
	], debug=False)

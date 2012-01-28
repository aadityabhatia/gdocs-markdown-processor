from google.appengine.api import memcache, users
import logging

class RpcMethods:

	def __init__(self):
		pass

	def clearCache(self):
		if not users.is_current_user_admin():
			logging.warn("Access denied: %s", users.get_current_user())
			return False
		return memcache.Client().flush_all()

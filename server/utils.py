import sys
sys.path.insert(0, 'distlib.zip')

from google.appengine.api import memcache, urlfetch
import config
import html2text
import logging
import markdown
import time

def getContentObj(key):

	# TODO: enhance expiry mechanism - retain content until updated

	memcacheClient = memcache.Client()
	cacheEntry = memcacheClient.get(key)
	if cacheEntry:
		return cacheEntry
	else:
		logging.info("fetching: %s", (config.contentURL % key))
		result = urlfetch.fetch(config.contentURL % key)

		if result.status_code != 200 and result.status_code != 304:
			return None

		badHTML = result.content
		text = html2text.html2text(badHTML)
		content = processHtml(markdown.markdown(text))

		doc = {'content': content, 'timestamp': int(time.time())}
		memcacheClient.set(key, doc, config.contentCacheDuration)
		return doc

def processHtml(html):
	return html.replace('h4>', 'h5>').replace('h3>', 'h4>').replace('h2>', 'h3>').replace('h1>', 'h2>').replace('<ul>', "<ul class='disc'>")

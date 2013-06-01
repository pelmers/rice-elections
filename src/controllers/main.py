"""
The Rice Elections App.
"""

__author__ = 'Waseem Ahmad <waseem@rice.edu>'


import logging
import json
import webapp2

from google.appengine.api import users
from models import models
from utils import BasePageHandler

providers = {
    'signin_google'   : 'https://www.google.com/accounts/o8/id',
    'signin_yahoo'    : 'yahoo.com',
    'signin_aol'      : 'aol.com'
}

class IndexHandler(BasePageHandler):
    """Handles the main page."""
    def get(self):
        page_data = {}
        for provider, url in providers.items():
            page_data[provider] = users.create_login_url('/admin',
                                                         federated_identity=url)
        return self.render_template('/home', page_data)

class StaticHandler(BasePageHandler):
    """Handles GET requests for static pages."""
    def get(self):
        return self.render_template(self.request.path, {})

class VotesCountHandler(BasePageHandler):
    def get(self):
        votes_count = models.get_vote_count()
        return webapp2.Response(json.dumps({'votes_count': votes_count}))


app = webapp2.WSGIApplication([
    ('/', IndexHandler),
    ('/stats/votes-count', VotesCountHandler),
    ('/.*', StaticHandler)
], debug=True)

"""
The Rice Elections App.
"""

__author__ = 'Waseem Ahmad <waseem@rice.edu>'


import logging
import json
import webapp2

from models import models
from utils import BasePageHandler

class IndexHandler(BasePageHandler):
    """Handles the main page."""
    def get(self):
        return self.render_template('/home', {})

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

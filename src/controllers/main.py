"""
The Rice Elections App.
"""

__author__ = 'Waseem Ahmad <waseem@rice.edu>'


import logging
import json
import webapp2

from models import models
from models.webapputils import render_template, json_response

class IndexHandler(webapp2.RequestHandler):
    """Handles the main page."""
    def get(self):
        return render_template('/home', {})

class StaticHandler(webapp2.RequestHandler):
    """Handles GET requests for static pages."""
    def get(self):
        return render_template(self.request.path, {})

class VotesCountHandler(webapp2.RequestHandler):
    def get(self):
        votes_count = models.get_vote_count()
        return webapp2.Response(json.dumps({'votes_count': votes_count}))


app = webapp2.WSGIApplication([
    ('/', IndexHandler),
    ('/stats/votes-count', VotesCountHandler),
    ('/.*', StaticHandler)
], debug=True)

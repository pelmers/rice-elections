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

class RegistrationHandler(BasePageHandler):
  def get(self):
    return self.render_template('/register', {})

app = webapp2.WSGIApplication([
  ('/register.*', RegistrationHandler)
], debug=True)
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
    page_data = {
      'universities': [
        {'id': 12345, 'name': 'Rice University', 'supported': True},
        {'id': 12346, 'name': 'Columbia University', 'supported': False}
      ],
      'email': models.get_current_user().email(),
      'nickname': models.get_current_user().nickname()
    }
    return self.render_template('/register', page_data)

app = webapp2.WSGIApplication([
  ('/register.*', RegistrationHandler)
], debug=True)
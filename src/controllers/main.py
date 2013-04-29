"""
The Rice Elections App.
"""

__author__ = 'Waseem Ahmad <waseem@rice.edu>'


import logging
import json
import webapp2

from models import models
import utils
from utils import render_template, json_response

app = utils.App(debug=True)

@app.route('/')
def index(request):
    """Handle the main page."""
    return render_template('/home', {})

@app.route('/.*')
def static_page(request):
    """Handle GET requests for static pages."""
    return render_template(request.path, {})

@app.route('/stats/votes-count')
def votes_count(request):
    votes_count = models.get_vote_count()
    return json.dumps({'votes_count': votes_count})

"""
Controller for voting related requests.
"""

import webapp2

from authentication import auth

from models import webapputils

from models.vote import vote_data
from models.vote_.cast_ballot import BallotHandler
from models.vote_.view_results import result_data

class VoteHandler(webapp2.RequestHandler):
    """
    Handles GET requests for the Vote page.
    """

    def get(self):
        voter = auth.get_voter(self)
        page_data = vote_data(voter)
        webapputils.render_page(self, '/vote', page_data)

class ResultsHandler(webapp2.RequestHandler):
    """
    Handles GET requests for the Results page.
    """

    def get(self):
        """
        Serves the election data to the front-end for display.
        """
        voter = auth.get_voter(self)
        election_id = self.request.get('id')
        page_data = result_data(voter, election_id)
        webapputils.render_page(self, '/vote/view_results', page_data)

app = webapp2.WSGIApplication([
    ('/vote', VoteHandler),
    ('/vote/cast-ballot', BallotHandler),
    ('/vote/view-results', ResultsHandler)
], debug=True)

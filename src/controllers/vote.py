"""
Controller for voting related requests.
"""

import json
import webapp2

from authentication import auth

from models.webapputils import render_template

from models.vote import election_list_data
from models.vote_.cast_ballot import ballot_data, cast_ballot
from models.vote_.view_results import result_data

class VoteHandler(webapp2.RequestHandler):
    """
    Handles GET requests for the Vote page.
    """

    def get(self):
        """
        Serves all the votes that this voter can see.
        """
        voter = auth.get_voter(self)
        page_data = election_list_data(voter)
        return render_template('/vote', page_data)

class BallotHandler(webapp2.RequestHandler):
    """
    Handles GET requests for the Vote page.
    """

    def get(self):
        """
        Serves the empty ballot to the client-side so that the user may fill it out and submit it back via post.
        """
        voter = auth.get_voter(self)
        election_id = self.request.get('id')
        try:
            page_data = ballot_data(voter, election_id)
        except AssertionError as e:
            page_data = {'error_msg': e.message}
        return render_template('/vote/cast-ballot', page_data)
    
    def post(self):
        """
        Takes the filled out ballot from the client-side, validates it, and stores it in the models.
        Sends confirmation to client-side.
        """
        formData = json.loads(self.request.get('formData'))

        voter = auth.get_voter()
        election_id = formData['election_id']
        positions = formData['positions']

        try:
            cast_ballot(voter, election_id, positions)
            status = 'OK'
            message = 'Your ballot has been successfully cast! <a href="/vote">Click here to go to the voting page.</a>'
        except AssertionError as e:
            status = 'ERROR'
            message = e.message
        self.response.write(json.dumps({'status': status, 'msg': message}))

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
        try:
            page_data = result_data(voter, election_id)
        except AssertionError as e:
            page_data = {'error_msg': e.message}
        return render_template('/vote/view-results', page_data)

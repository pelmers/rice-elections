"""
An API for handling elections.
"""

import json
import logging
import webapp2

from authentication import auth
from datetime import datetime
from models import models, tasks
from controllers.utils import BaseHandler


class ElectionsHandler(BaseHandler):

    def authenticate(self, organization):
        voter = auth.get_voter()
        status = models.get_admin_status(voter, organization)
        if not status:
            self.abort(403)

    def get(self, election_id):
        # Authenticate
        election = models.Election.get(election_id)
        organization = election.organization
        self.authenticate(organization)

        return self.json_respond('ok', 'Election found', election.to_json())

    def post(self):
        # Authenticate
        data = json.loads(self.request.body)
        organization = models.Organization.get(data['organization_id'])
        self.authenticate(organization)
        
        election = models.Election(
            name=data['name'],
            start=datetime.fromtimestamp(data['times']['start']),
            end=datetime.fromtimestamp(data['times']['end']),
            organization=organization,
            universal=data['universal'],
            hidden=data['hidden'],
            result_delay=data['result_delay'])
        election.put()
        logging.info('Election created. Organization: %s Name: %s',
                     organization.name, election.name)
        return self.json_respond('ok', 'Created', election.to_json())

    def put(self, election_id):
        # Authenticate
        data = json.loads(self.request.body)
        organization = models.Organization.get(data['organization_id'])
        self.authenticate(organization)

        election = models.Election.get(election_id)
        election.name = data['name']
        election.start = datetime.fromtimestamp(data['times']['start'])
        election.end = datetime.fromtimestamp(data['times']['end'])
        election.universal = data['universal']
        election.hidden = data['hidden']
        election.result_delay = data['result_delay']
        election.put()
        return json_response('ok', 'Updated', election.to_json())

app = webapp2.WSGIApplication([
    webapp2.Route('/api/elections', handler=ElectionsHandler, name='elections'),
    webapp2.Route('/api/elections/<election_id>',
                  handler=ElectionsHandler,
                  name='election')
], debug=True)
"""
Controller for tasks.
Routed through here for security reasons, ensures the tasks were internally
generated and not by a user.
"""

import json
import logging
import webapp2

from datetime import datetime
from models import models, report_results


class ElectionTaskHandler(webapp2.RequestHandler):

    def post(self):
        methods = {
            'compute_results': self.compute_results
        }

        # Get data
        data = json.loads(self.request.get('data'))
        election = models.Election.get(data['election_key'])
        method = data['method']

        # Get the method
        if method in methods:
            methods[method](election)
        else:
            logging.error('Unknown method: %s. Task failed!', method)

    def compute_results(self, election):
        # Assert validity
        if not election:
            logging.error('Election not found.')
            return
        if election.end > datetime.now():
            logging.error('Election is still open.')
            return
        if election.result_computed:
            logging.error('Election results already computed.')
            return

        logging.info('Computing results for election: %s, organization: %s.', 
                        election.name, election.organization.name)

        for election_position in election.election_positions:
            logging.info('Computing election position: %s',
                            election_position.position.name)
            election_position.compute_winners()

        election.result_computed = True
        election.put()
        logging.info('Computed results for election: %s, organization: %s.',
                        election.name, election.organization.name)

        admin_emails = []
        for org_admin in election.organization.organization_admins:
            admin_emails.append(org_admin.admin.email)
        report_results.email_report(admin_emails, election)

class ElectionVotersTaskHandler(webapp2.RequestHandler):

    def post(self):
        methods = {
            'add_voters': self.add_voters,
            'delete_voters': self.delete_voters
        }

        # Get data
        data = json.loads(self.request.get('data'))
        election = models.Election.get(data['election_key'])
        voters = data['voters']
        method = data['method']

        # Get the method
        if method in methods:
            methods[method](election, voters)
        else:
            logging.error('Unknown method: %s. Task failed!', method)

    def add_voters(self, election, voters):
        models.add_eligible_voters(election, voters)
        models.update_voter_set(election)
        

    def delete_voters(self, election, voters):
        models.remove_eligible_voters(election, voters)
        models.update_voter_set(election)
        

app = webapp2.WSGIApplication([
    ('/tasks/admin/organization/election/information', ElectionTaskHandler),
    ('/tasks/admin/organization/election/voters', ElectionVotersTaskHandler)
], debug=True)
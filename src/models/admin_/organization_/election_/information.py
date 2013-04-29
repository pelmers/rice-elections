"""
Back end for election panel information.
"""

__author__ = 'Waseem Ahmad <waseem@rice.edu>'

import json
import logging
import webapp2

from authentication import auth
from datetime import datetime, timedelta
from google.appengine.api import taskqueue
from models import models, report_results, tasks
from models.webapputils import render_template
from models.webapputils import json_response
from models.admin_.organization_.election import get_panel

PAGE_URL = '/admin/organization/election/information'
TASK_URL = '/tasks/admin/organization/election/information'

class ElectionInformationHandler(webapp2.RequestHandler):

    def get(self):
        # Authenticate user
        voter = auth.get_voter(self)
        status = models.get_admin_status(voter)
        if not status:
            return render_template('/templates/message', 
                {'status': 'Error', 'msg': 'Not Authorized'})
        
        data = {}

        # Get election
        election = auth.get_election()
        if election:
            data = {'id': str(election.key()),
                    'election': election.to_json()}
        return get_panel(PAGE_URL, data, data.get('id'))

    def post(self):
        methods = {
            'get_election': self.get_election,
            'update_election': self.update_election
        }

        # Authenticate user
        org = auth.get_organization()
        if not org:
            return json_response('ERROR', 'Not Authorized')

        # Get election
        election = auth.get_election()

        # Get the method
        data = json.loads(self.request.get('data'))
        method = data['method']
        logging.info('Method: %s\n Data: %s', method, data)
        if method in methods:
            methods[method](election, data)
        else:
            return json_response('ERROR', 'Unkown method')

    def get_election(self, election, data):
        out = {'status': 'OK'}
        if election:
            out['election'] = election.to_json()
        self.response.write(json.dumps(out))

    def update_election(self, election, data):
        out = {'status': 'OK'}
        if not election:
            # User must be trying to create new election
            election = models.Election(
                name=data['name'],
                start=datetime.fromtimestamp(data['times']['start']),
                end=datetime.fromtimestamp(data['times']['end']),
                organization=auth.get_organization(),
                universal=data['universal'],
                hidden=data['hidden'],
                result_delay=data['result_delay'])
            election.put()
            out['msg'] = 'Created'
            auth.set_election(election)
        else:
            election.name = data['name']
            election.start = datetime.fromtimestamp(data['times']['start'])
            election.end = datetime.fromtimestamp(data['times']['end'])
            election.universal = data['universal']
            election.hidden = data['hidden']
            election.result_delay = data['result_delay']
            election.put()
            out['msg'] = 'Updated'
        tasks.schedule_result_computation(election, TASK_URL)
        out['election'] = election.to_json()
        self.response.write(json.dumps(out))

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

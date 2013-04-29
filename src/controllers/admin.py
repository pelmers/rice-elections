"""
Controller for admin related requests.
"""

import json
import logging
import webapp2

from authentication import auth
from models import models, tasks
from models.webapputils import render_template, json_response
from models.admin_.organization_.election import get_panel

VOTER_PAGE_URL = '/admin/organization/election/voters'
VOTER_TASK_URL = '/tasks/admin/organization/election/voters'
MSG_NOT_AUTHORIZED = ('We\'re sorry, you\'re not an organization administrator. Please contact the website administration '
                     'if you are interested in conducting elections for your organization.')

from models.admin_.organization_.election import ElectionPanelHandler
from models.admin_.organization_.election_.information import ElectionInformationHandler
from models.admin_.organization_.election_.positions import ElectionPositionsHandler

class OrganizationPanelHandler(webapp2.RequestHandler):

    def get(self):
        # Authenticate user
        voter = auth.get_voter(self)
        status = models.get_admin_status(voter)
        if not status:
            logging.info('Not authorized')
            return render_template('/templates/message',
                {'status': 'Not Authorized', 'msg': MSG_NOT_AUTHORIZED})

        # Get organization information
        admin = models.Admin.gql('WHERE voter=:1', voter).get()
        logging.info(admin)
        org_admin = models.OrganizationAdmin.gql('WHERE admin=:1',
                                                    admin).get()
        logging.info(org_admin)
        if not org_admin:
            logging.info('Not authorized')
            return render_template('/templates/message',
                {'status': 'Not Authorized', 'msg': MSG_NOT_AUTHORIZED})
        org = org_admin.organization
        auth.set_organization(org)

        # Construct page information
        page_data = {}
        page_data['organization'] = org
        page_data['admins'] = models.admin_list(org)
        page_data['elections'] = [elec.to_json() for elec in org.elections]
        logging.info(page_data['elections'])
        logging.info(page_data)
        return render_template('/admin/organization', page_data)

    def post(self):
        # Authenticate user
        voter = auth.get_voter()
        if not voter:
            return json_response('ERROR', MSG_NOT_AUTHORIZED)
        status = models.get_admin_status(voter)
        if not status:
            return json_response('ERROR', MSG_NOT_AUTHORIZED)

        # Get method and data
        logging.info('Received call')
        data = json.loads(self.request.get('data'))
        methods = {'update_profile': self.update_profile}
        methods[data['method']](data['data'])

    def update_profile(self, data):
        """
        Updates the organization profile.
        """
        logging.info('Updating profile')
        org_id = data['id']
        org = models.Organization.get(org_id)
        assert models.get_admin_status(auth.get_voter(), org)
        for field in ['name', 'description', 'website']:
            setattr(org, field, data[field].strip())
        org.put()
        return json_response('OK', 'Updated')

class ElectionVotersHandler(webapp2.RequestHandler):

    def get(self):
        # Authenticate user
        voter = auth.get_voter(self)
        status = models.get_admin_status(voter)
        if not status:
            return render_template('/templates/message',
                {'status': 'Not Authorized', 'msg': MSG_NOT_AUTHORIZED})

        # Get election
        election = auth.get_election()
        if not election:
            return get_panel(
                VOTER_PAGE_URL,
                {'status': 'ERROR','msg': 'No election found.'},
                None)

        if election.universal:
            return get_panel(
                VOTER_PAGE_URL,
                {'status': 'Universal Election',
                 'msg': 'This is a universal election, anyone with a valid '
                        'NetID can vote for. Therefore you cannot manage '
                        'the voters list.'},
                None)

        data = {'status': 'OK',
                'id': str(election.key()),
                'voters': sorted(list(models.get_voter_set(election)))}
        logging.info(data)
        return get_panel(VOTER_PAGE_URL, data, data.get('id'))

    def post(self):
        methods = {
            'add_voters': self.add_voters,
            'delete_voters': self.delete_voters
        }

        # Get election
        election = auth.get_election()
        if not election:
            return

        # Get the method
        data = json.loads(self.request.get('data'))
        method = data['method']
        logging.info('Method: %s\n Data: %s', method, data)
        if method in methods:
            methods[method](election, data)
        else:
            return json_response('ERROR', 'Unknown method')

    def add_voters(self, election, data):
        tasks.voters_task(election, data, 'add_voters', VOTER_TASK_URL)
        voter_set = models.get_voter_set(election)
        for voter in data['voters']:
            voter_set.add(voter)
        out = {'status': 'OK',
               'msg': 'Adding',
               'voters': sorted(list(voter_set))}
        self.response.write(json.dumps(out))

    def delete_voters(self, election, data):
        tasks.voters_task(election, data, 'delete_voters', VOTER_TASK_URL)
        voter_set = models.get_voter_set(election)
        for voter in data['voters']:
            voter_set.discard(voter)
        out = {'status': 'OK',
               'msg': 'Adding',
               'voters': sorted(list(voter_set))}
        self.response.write(json.dumps(out))

app = webapp2.WSGIApplication([
    ('/admin/organization', OrganizationPanelHandler),
    ('/admin/organization/election', ElectionPanelHandler),
    ('/admin/organization/election/information', ElectionInformationHandler),
    ('/admin/organization/election/positions', ElectionPositionsHandler),
    ('/admin/organization/election/voters', ElectionVotersHandler),
    ('/admin/organization/election/.*', ElectionPanelHandler)
], debug=True)

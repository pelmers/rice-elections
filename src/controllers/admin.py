"""
Controller for admin related requests.
"""

import json
import logging
import webapp2

from authentication import auth
from datetime import datetime
from models import models, tasks
from models.webapputils import render_template, json_response
from models.admin_.organization_.election import get_panel

INFO_TASK_URL = '/tasks/admin/organization/election/information'
VOTER_TASK_URL = '/tasks/admin/organization/election/voters'
MSG_NOT_AUTHORIZED = ('We\'re sorry, you\'re not an organization administrator. Please contact the website administration '
                     'if you are interested in conducting elections for your organization.')

from models.admin_.organization_.election import ElectionPanelHandler

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
        page_url = '/admin/organization/election/information'
        if election:
            data = {'id': str(election.key()),
                    'election': election.to_json()}
        return get_panel(page_url, data, data.get('id'))

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
        tasks.schedule_result_computation(election, INFO_TASK_URL)
        out['election'] = election.to_json()
        self.response.write(json.dumps(out))

class ElectionPositionsHandler(webapp2.RequestHandler):

    def get(self):
        # Authenticate user
        voter = auth.get_voter(self)
        status = models.get_admin_status(voter)
        if not status:
            return render_template('/templates/message',
                {'status': 'ERROR', 'msg': 'Not Authorized'})

        # Get election
        election = auth.get_election()
        page_url = '/admin/organization/election/positions'
        if not election:
            return get_panel(
                page_url,
                {'status': 'ERROR','msg': 'No election found.'},
                None)

        data = {'status': 'OK',
                'id': str(election.key()),
                'election': election.to_json()}
        return get_panel(page_url, data, data.get('id'))

    def post(self):
        methods = {
            'get_positions': self.get_positions,
            'add_position': self.add_position,
            'get_position': self.get_position,
            'update_position': self.update_position,
            'delete_position': self.delete_position
        }

        # Get election
        election = auth.get_election()
        logging.info('Election: %s\n', election.name)
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

    def get_positions(self, election, data):
        out = {'positions': [p.to_json() for p in election.election_positions]}
        self.response.write(json.dumps(out))

    def add_position(self, election, data):
        position = data['position']
        position_entry = models.get_position(position['name'],
                                             election.organization,
                                             create=True)

        # Store position
        if position['type'] == 'Ranked-Choice':
            ep = models.RankedVotingPosition(
                election=election,
                position=position_entry,
                vote_required=position['vote_required'],
                write_in_slots=position['write_in_slots'])
            ep.put()
        elif position['type'] == 'Cumulative-Voting':
            ep = models.CumulativeVotingPosition(
                election=election,
                position=position_entry,
                vote_required=position['vote_required'],
                write_in_slots=position['write_in_slots'],
                points=position['points'],
                slots=position['slots'])
            ep.put()

        # Store candidates
        for candidate in position['candidates']:
            models.ElectionPositionCandidate(
                election_position=ep,
                name=candidate['name']).put()

        out = {'status': 'OK',
               'msg': 'Created',
               'position': ep.to_json()}
        self.response.write(json.dumps(out))

    def get_position(self, election, data):
        ep = models.ElectionPosition.get(data['id'])
        if ep:
            self.response.write(json.dumps({'position': ep.to_json()}))
            logging.info(ep.to_json())
        else:
            return json_response('ERROR', 'Not found')

    def update_position(self, election, data):
        logging.info("Election: ", election)
        logging.info("Data: ", data)
        return json_response('ERROR', 'Feature not available')

    def delete_position(self, election, data):
        ep = models.ElectionPosition.get(data['id'])
        if ep:
            for epc in ep.election_position_candidates:
                epc.delete()
            ep.delete()
            return json_response('OK', 'Deleted')
        else:
            return json_response('ERROR', 'Not found')

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
        page_url = '/admin/organization/election/voters'
        if not election:
            return get_panel(
                page_url,
                {'status': 'ERROR','msg': 'No election found.'},
                None)

        if election.universal:
            return get_panel(
                page_url,
                {'status': 'Universal Election',
                 'msg': 'This is a universal election, anyone with a valid '
                        'NetID can vote for. Therefore you cannot manage '
                        'the voters list.'},
                None)

        data = {'status': 'OK',
                'id': str(election.key()),
                'voters': sorted(list(models.get_voter_set(election)))}
        logging.info(data)
        return get_panel(page_url, data, data.get('id'))

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

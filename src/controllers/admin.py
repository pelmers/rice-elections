"""
Controller for admin related requests.
"""

import json
import logging
import webapp2

from authentication import auth
from models import models
from models.webapputils import render_template, json_response

MSG_NOT_AUTHORIZED = ('We\'re sorry, you\'re not an organization administrator. Please contact the website administration '
                     'if you are interested in conducting elections for your organization.')

from models.admin_.organization_.election import ElectionPanelHandler
from models.admin_.organization_.election_.information import ElectionInformationHandler
from models.admin_.organization_.election_.positions import ElectionPositionsHandler
from models.admin_.organization_.election_.voters import ElectionVotersHandler

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

app = webapp2.WSGIApplication([
    ('/admin/organization', OrganizationPanelHandler),
    ('/admin/organization/election', ElectionPanelHandler),
    ('/admin/organization/election/information', ElectionInformationHandler),
    ('/admin/organization/election/positions', ElectionPositionsHandler),
    ('/admin/organization/election/voters', ElectionVotersHandler),
    ('/admin/organization/election/.*', ElectionPanelHandler)
], debug=True)

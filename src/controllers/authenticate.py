"""
Controller for authentication related requests.
"""

import webapp2

import logging
import re
import urllib
import webapp2

from authentication.gaesessions import get_current_session, delete_expired_sessions
from authentication.auth import CAS_SERVER
from models import models
from models.webapputils import render_page

class LoginResponseHandler(webapp2.RequestHandler):
    """Receive the response from CAS after the user authentication."""

    def get(self):
        ticket = self.request.get('ticket')

        if not ticket:
            render_page(self, '/templates/message', {'status': 'Error', 'msg': 'Ticket not specified.'})
            return

        net_id = self.validate_cas_2()
        if not net_id:
            render_page(self, '/templates/message', {'status': 'Error', 'msg': 'Invalid ticket. Credentials not verified.'})
            return

        # Close any active session the user has since credentials have been freshly verified.
        session = get_current_session()
        if session.is_active():
            session.terminate()

        # Get the user's record
        voter = models.get_voter(net_id, create=True)

        # Start a session for the user
        session['net_id'] = voter.net_id

        destination_url = str(self.request.get('destination'))
        if not destination_url:
            render_page(self, '/templates/message', {'status': 'Error', 'msg': 'User authenticated. However, no destination '
                              'url is provided.'})
            return

        logging.info('Redirecting to %s', destination_url)
        self.redirect(destination_url)

    def validate_cas_2(self):
        """
        Validate the given ticket using CAS 2.0 protocol.

        Returns:
            net_id {String}: the id of the user. None if ticket invalid.
        """
        ticket = self.request.get('ticket')
        service_url = self.remove_parameter_from_url(self.request.url, 'ticket')        # Strip ticket parameter
        cas_validate = CAS_SERVER + '/cas/serviceValidate?ticket=' + ticket + '&service=' + service_url

        # Ask CAS server whether this ticket is valid
        f_validate = urllib.urlopen(cas_validate)

        # Get the first line - should be yes or no
        response = f_validate.read()
        net_id = self.parse_tag(response, 'cas:user')
        if not net_id:
            logging.info('Invalid ticket.')
            return None

        logging.info('Ticket validated for %s', net_id)
        return net_id

    @staticmethod
    def parse_tag(string, tag):
        """
        Used for parsing XML. Searches the string for first occurrence of <tag>...</tag>.

        Returns:
            The trimmed text between tags. "" if tag is not found.
        """
        tag1_pos1 = string.find("<" + tag)
        #  No tag found, return empty string.
        if tag1_pos1==-1: return ""
        tag1_pos2 = string.find(">",tag1_pos1)
        if tag1_pos2==-1: return ""
        tag2_pos1 = string.find("</" + tag,tag1_pos2)
        if tag2_pos1==-1: return ""
        return string[tag1_pos2+1:tag2_pos1].strip()

    @staticmethod
    def remove_parameter_from_url(url, parameter):
        """
        Removes the specified parameter from the url. Returns url as is if parameter doesn't exist.

        Args:
            url {String}: input url
            parameter {String}: parameter to remove.
        Returns:
            {String}: url with ticket parameter removed.
        """
        return re.sub('&%s(=[^&]*)?|%s(=[^&]*)?&?' % (parameter, parameter), '', url)


class LogoutHandler(webapp2.RequestHandler):
    def get(self):
        """Logs out the user from CAS."""
        app_url = self.request.headers.get('host', 'no host')    # URL of the app itself
        service_url = 'http://%s/authenticate/logout-response' % app_url
        self.redirect(CAS_SERVER + '/cas/logout?service=' + service_url)


class LogoutResponseHandler(webapp2.RequestHandler):
    def get(self):
        """Logs out the user."""
        session = get_current_session()
        if session.has_key('net_id'):
            session.terminate()
            render_page(self, '/templates/message', {'status': 'Logged Out', 'msg': 'You\'ve been logged out. See you again soon!'})
        else:
            render_page(self, '/templates/message', {'status': 'Silly', 'msg': 'You weren\'t logged in.'})

class CleanupSessionsHandler(webapp2.RequestHandler):
    def get(self):
        while not delete_expired_sessions():
            pass

app = webapp2.WSGIApplication([
    ('/authenticate/login-response', LoginResponseHandler),
    ('/authenticate/logout', LogoutHandler),
    ('/authenticate/logout-response', LogoutResponseHandler),
    ('/authenticate/cleanup-sessions', CleanupSessionsHandler)
], debug=True)

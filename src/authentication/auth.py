"""
Application specific authentication module.
"""

__author__ = 'Waseem Ahmad <waseem@rice.edu>'

from gaesessions import get_current_session
from models import models

CAS_SERVER  = "https://netid.rice.edu"

def redirect_to_cas(request_handler):
    """
    Redirects client to CAS server for credentials verification.
    """

def require_login(request_handler):
    """
    Requires the user to be logged in through NetID authentication.

    Args:
        request_handler: webapp2 request handler of the user request
    """
    destination_url = request_handler.request.url
    app_url = request_handler.request.headers.get('host', 'no host')    # URL of the app itself
    service_url = 'http://%s/authenticate/login-response' % app_url
    cas_url = CAS_SERVER + '/cas/login?service=' + service_url + '?destination=' + destination_url
    request_handler.redirect(cas_url, abort=True)

def get_voter(handler=None):
    """
    Returns the voter from user session.

    Args:
        handler {webapp2.RequestHandler}: Redirects the user to login if the
            user is not logged in. Note: Redirects only work for GET requests.

    Returns:
        voter: the Voter if authenticated. None otherwise.
    """
    session = get_current_session()
    if session.has_key('net_id'):
        return models.get_voter(session['net_id'])
    elif handler:
        require_login(handler)
    else:
        return None

def set_organization(organization):
    """
    Sets the specified organization for reference for the logged in admin.

    Args:
        organization {Organization}: the organization to set.
    """
    session = get_current_session()
    session['_organization'] = str(organization.key())

def get_organization():
    """
    Gets the organization from the admin session.

    Returns:
        organization {Organization}: the Organization that the admin is working
            with.
    """
    session = get_current_session()
    if session.has_key('_organization'):
        return models.Organization.get(session['_organization'])
    else:
        return None

def set_election(election):
    """
    Sets the specified election for reference for the logged in admin.

    Args:
        election {Election}: the election to set.
    """
    session = get_current_session()
    session['_election'] = str(election.key())

def clear_election():
    """
    Clears the election from admin session data.
    """
    session = get_current_session()
    if session.has_key('_election'):
        del session['_election']

def get_election():
    """
    Gets the election from the admin session.

    Returns:
        election {Election}: the Election the the admin is working with.
    """
    session = get_current_session()
    if session.has_key('_election'):
        return models.Election.get(session['_election'])
    else:
        return None

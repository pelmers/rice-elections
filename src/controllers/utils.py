"""
Utility functions for webapp2.
"""

__author__ = 'Waseem Ahmad <waseem@rice.edu>'

import datetime
import os
import jinja2
import json

import webapp2

from authentication.gaesessions import get_current_session

MAIN_DIR = os.path.dirname(__file__)
PAGES_DIR = os.path.join(MAIN_DIR, '../views')

JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(PAGES_DIR))

NAV_BAR = [
    {'text': 'Home', 'link': '/home'},
    {'text': 'Vote', 'link': '/vote'},
    {'text': 'Admin', 'link': '/admin/organization'},
    {'text': 'Contact', 'link': '/contact'}]

class App(webapp2.WSGIApplication):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        self.router.set_dispatcher(self.__class__.custom_dispatcher)

    @staticmethod
    def custom_dispatcher(router, request, response):
        rv = router.default_dispatcher(request, response)
        if isinstance(rv, basestring):
            rv = webapp2.Response(rv)
        elif isinstance(rv, tuple):
            rv = webapp2.Response(*rv)

        return rv

    def route(self, *args, **kwargs):
        def wrapper(func):
            self.router.add(webapp2.Route(handler=func, *args, **kwargs))
            return func
        
        return wrapper

def format_datetime(value, format):
    if format == 'medium':
        return value.strftime('%a, %B %d, %Y, %I:%M %p') + ' UTC'
    if format == 'small':
        return value.strftime('%m/%d/%y %I:%M %p') + ' UTC'

def render_template(page_name, page_data):
    JINJA_ENV.filters['datetime'] = format_datetime
    JINJA_ENV.globals['now'] = str(datetime.datetime.now())

    try:
        template = JINJA_ENV.get_template(page_name + '.html')
    except jinja2.TemplateNotFound:
        template = JINJA_ENV.get_template('templates/not-found.html')

    # Mark all links in the nav bar as inactive except the page open
    for item in NAV_BAR:
        item['active'] = (item['link'] == page_name)

    page_data['nav_bar'] = NAV_BAR
    
    # If logged in, display NetID with logout option
    session = get_current_session()
    if session.has_key('net_id'):
        page_data['net_id'] = session['net_id']

    return template.render(page_data)

def json_response(status, message):
    """
    Sends a response to the front-end. Used for AJAX responses.
    
    Args:
    	handler {webapp2.RequestHandler}: request handler
        status {String}: response status
        message {String}: response message
    """
    return json.dumps({'status': status, 'msg': message})

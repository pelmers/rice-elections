"""
Utility functions for webapp2.
"""

__author__ = 'Waseem Ahmad <waseem@rice.edu>'

import datetime
import os
import jinja2
import json
import logging
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

class BaseAPIHandler(webapp2.RequestHandler):
    def handle_exception(self, exception, debug):
        logging.exception(exception)

        self.json_respond('error', str(exception))
        if isinstance(exception, webapp2.HTTPException):
            self.response.set_status(exception.code)
        else:
            self.response.set_status(500)

    def json_respond(self, status, message, data=None):
        """
        Sends a response to the front-end. Used for AJAX responses.
        
        Args:
            status {String}: response status type
            message {String}: response status message

        """
        out = {'status': {'type': status, 'msg': message}}
        if data:
            out['data'] = data
        self.response.headers["Content-Type"] = "application/json"
        return self.response.write(json.dumps(out))

class BasePageHandler(webapp2.RequestHandler):
    def handle_exception(self, exception, debug):
        logging.exception(exception)
        msg = {'status': 'Error', 'msg': str(exception)}
        return BasePageHandler.render_template('templates/message', msg)

    @staticmethod
    def format_datetime(value, format):
        if format == 'medium':
            return value.strftime('%a, %B %d, %Y, %I:%M %p') + ' UTC'
        if format == 'small':
            return value.strftime('%m/%d/%y %I:%M %p') + ' UTC'

    @staticmethod
    def render_template(page_name, page_data):
        JINJA_ENV.filters['datetime'] = BasePageHandler.format_datetime
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

        return webapp2.Response(template.render(page_data))
"""
Back-end for serving the results of an election.
"""

__authors__ = ['Waseem Ahmad <waseem@rice.edu>',
               'Andrew Capshaw <capshaw@rice.edu>']

import models
import logging
import webapp2

from authentication import auth
from datetime import datetime, timedelta
from models import models, webapputils

def result_data(voter, election_id):

    page_data = {}

    # Authenticate user
    net_id = voter.net_id

    # Serve the election the user has requested
    if not election_id:
        page_data['error_msg'] = 'No election was specified.'
        return page_data
    logging.info('%s requested election: %s', net_id, election_id)

    # Get the election from the database
    election = models.Election.get(election_id)
    if not election:
        page_data['error_msg'] = 'Election not found.'
        return page_data
    
    # Make sure user is eligible to vote
    status = models.voter_status(voter, election)
    if status != 'invalid_time' and not models.get_admin_status(voter, election.organization):
        page_data['error_msg'] = 'You are not eligible to view results.'
        return page_data
    
    if not election.result_computed:
        page_data['error_msg'] = 'Election results are not available yet.'
        return page_data
    
    public_result_time = election.end
    if election.result_delay:
        public_result_time += timedelta(seconds=election.result_delay)
        
    if datetime.now() < public_result_time:
        # Check to see if the user is an election admin
        status = models.get_admin_status(voter, election.organization)
        if not status:
            page_data['error_msg'] = ('Election results are not available to the public yet. '
                                     'Please wait for %s longer.' % 
                                     str(public_result_time - datetime.now())[:6])
            return page_data

    # Write election information
    for key, value in election.to_json().items():
        page_data[key] = value
    page_data['voter_net_id'] = voter.net_id
    page_data['positions'] = []
    
    # Write position information
    election_positions = election.election_positions
    for election_position in election_positions:
        position = {}
        for key, value in election_position.to_json().items():
            position[key] = value
        page_data['positions'].append(position)

    logging.info(page_data)

    return page_data

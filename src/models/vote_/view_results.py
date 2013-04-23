"""
Back-end for serving the results of an election.
"""

__authors__ = ['Waseem Ahmad <waseem@rice.edu>',
               'Andrew Capshaw <capshaw@rice.edu>']

import models
import logging

from datetime import datetime, timedelta
from models import models

def result_data(voter, election_id):
    """
    Return the data for showing the results of the election.

    Throws:
        AssertionError
    """

    page_data = {}

    # Authenticate user
    net_id = voter.net_id

    # Serve the election the user has requested
    assert election_id, 'No election was specified.'
    logging.info('%s requested election: %s', net_id, election_id)

    # Get the election from the database
    election = models.Election.get(election_id)
    assert election, 'Election not found.'
    
    # Make sure user is eligible to vote
    status = models.voter_status(voter, election)
    assert status == 'invalid_time' or models.get_admin_status(voter, election.organization), 'You are not eligible to view results.'
    
    assert election.result_computed, 'Election results are not available yet.'
    
    public_result_time = election.end
    if election.result_delay:
        public_result_time += timedelta(seconds=election.result_delay)
        
    if datetime.now() < public_result_time:
        # Check to see if the user is an election admin
        status = models.get_admin_status(voter, election.organization)
        assert status, ('Election results are not available to the public yet. '
                        'Please wait for %s longer.' % 
                        str(public_result_time - datetime.now())[:6])

    # Write election information
    page_data.update(election.to_json())
    page_data['voter_net_id'] = voter.net_id
    page_data['positions'] = [dict(position.to_json()) 
                              for position in election.election_positions]

    logging.info(page_data)

    return page_data

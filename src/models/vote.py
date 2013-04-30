"""
Back-end for the vote page.
"""

__authors__ = ['Waseem Ahmad <waseem@rice.edu>',
               'Andrew Capshaw <capshaw@rice.edu>']

import logging

from authentication import auth
from google.appengine.ext import db
from datetime import datetime, timedelta
import models 

def election_list_data(voter):
    """
    Return the list of elections, open and closed, that this voter can see.

    Args:
        voter {Voter}: The current voter.

    Returns:
        A dictionary containing the open elections and election results
        that this voter can see.
    """

    page_data = {'open_elections': [], 'election_results': []}

    # Elections the user is eligible to vote for
    elections = voter.elections
    election_keys = [election.key() for election in elections]

    # Add universal elections
    universal_elections = models.Election.gql("WHERE universal=TRUE AND hidden=FALSE")
    for election in universal_elections:
        if datetime.now() < election.end and election.key() not in election_keys:
            elections.append(election)

    logging.info(elections)

    for election in elections:
        logging.info('Found election')
        data = {}
        data['id'] = str(election.key())
        data['name'] = election.name
        data['organization'] = election.organization.name
        now = datetime.now()
        if now > election.end:      # Election passed
            result_delay = election.result_delay
            data['end_date'] = election.end.strftime('%a, %B %d, %Y, %I:%M %p') + ' UTC'
            data['result_delay'] = result_delay

            # Compute how much time the user will have to wait to view the election
            time_since_election_end = (now - election.end).seconds + (now - election.end).days * 86400
            if time_since_election_end > result_delay:
                data['time_remaining'] = -1
            else:
                data['time_remaining'] = (result_delay - time_since_election_end) *1000
            page_data['election_results'].append(data)
        else:
            data['user_action'] = 'not_started' # Initial assumption

            # Check election times
            if election.start > now:
                start_str = election.start.strftime('%a, %B %d, %Y, %I:%M %p') + ' UTC'
                data['status'] = {'text': 'Voting begins on', 'date': start_str}
                data['user_action'] = 'not_started'
            else:
                end_str = election.end.strftime('%a, %B %d, %Y, %I:%M %p') + ' UTC'
                data['status'] = {'text': 'Voting ends on', 'date': end_str}
                data['user_action'] = 'vote'

            # Check to see if the user has already voted
            if models.voter_status(voter, election) == 'voted':
                data['user_action'] = 'voted'

            page_data['open_elections'].append(data)

        logging.info(data)

    return page_data

def ballot_data(voter, election_id):
    """
    Return the election data for this voter and election, or an error message.
    """
    page_data = {}

    # Authenticate user
    net_id = voter.net_id
    
    # Serve the election the user has requested
    assert election_id, 'No election was specified.'
    logging.info('%s requested election: %s', net_id, election_id)

    # Get the election from the database
    election = db.get(election_id)
    assert election, 'Election not found.'

    # Make sure user is eligible to vote
    status = models.voter_status(voter, election)
    assert status != 'voted', 'You have already voted for this election.'
    assert status != 'not_eligible', 'You are not eligible to vote for this election.'
    assert status != 'invalid_time', 'You are not in the eligible voting time for this election.'
    assert status == 'eligible', 'You are not eligible to vote for this election.'

    # Write election information
    page_data.update(election.to_json())
    page_data['positions'] = [dict(position.to_json()) 
                              for position in election.election_positions]
    page_data['voter_net_id'] = voter.net_id

    logging.info(page_data)

    return page_data

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

def cast_ballot(voter, election_id, positions):
    """
    Cast the ballot for the user given the positions array.
    """
    
    # Authenticate user
    assert voter, 'You\'re not logged in!'
    
    # Get the election from the database
    election = db.get(election_id)
    assert election, 'Invalid election!'
    # Make sure user is eligible to vote
    status = models.voter_status(voter, election)
    assert status != 'voted', 'You have already voted for this election.'
    assert status != 'not_eligible', 'You are not eligible to vote for this election.'
    assert status != 'invalid_time', 'You are not in the eligible voting time for this election.'
    assert status == 'eligible', 'You are not eligible to vote for this election.'
    
    # Verify that the user has voted correctly
    verified_positions = {}           # Whether an election_position has been verified
    for election_position in election.election_positions:
        verified_positions[str(election_position.key())] = False
    
    for position in positions:
        if position['type'] == 'Ranked-Choice':
            verified_positions[position['id']] = verify_ranked_choice_ballot(position)
        elif position['type'] == 'Cumulative-Voting':
            verified_positions[position['id']] = verify_cumulative_voting_ballot(position)
        else:
            logging.error('Encountered unknown position type: %s', position['type'])
            verified_positions[position['id']] = False
    
    logging.info('Verified Positions: %s', verified_positions)
    for verified in verified_positions.values():
        assert verified != False, 'You have attempted to cast an invalid ballot. Please verify that you are following all instructions.'
    
    # Record all of the votes
    for position in positions:
        if verified_positions[position['id']]:
            if position['type'] == 'Ranked-Choice':
                cast_ranked_choice_ballot(position)
            elif position['type'] == 'Cumulative-Voting':
                cast_cumulative_voting_ballot(position)
        
    models.mark_voted(voter, election)
    
def verify_ranked_choice_ballot(position):
    """
    Verifies the validity a ranked choice ballot.
    
    Args:
        position{dictionary}: the position dictionary from the client
    
    Returns:
        True if valid, False if invalid. None if empty ballot.
    """
    logging.info('Verifying ranked choice ballot.')
    election_position = models.RankedVotingPosition.get(position['id'])
    if not election_position:
        logging.info('No election position found in models.')
        return False
    assert election_position.position_type == 'Ranked-Choice'
    
    required = election_position.vote_required
    election_position_candidates = models.ElectionPositionCandidate.gql('WHERE election_position=:1 AND written_in=False',
                                                                election_position)
    num_ranks_required = election_position_candidates.count()
    write_in_slots_allowed = election_position.write_in_slots
    write_in_slots_used = 0
    ranks = []
    candidates_verified = {}
    for election_position_candidate in election_position_candidates:
        candidates_verified[str(election_position_candidate.key())] = False
    for candidate_ranking in position['candidate_rankings']:
        if not candidate_ranking['rank']:
            if required: 
                logging.info('Ranking required but not provided')
                return False   # Ranking required but not provided
            else: return None           # Empty ballot
        else:
            ranks.append(candidate_ranking['rank'])
            candidates_verified[candidate_ranking['id']] = True
            if candidate_ranking['id'].startswith('write-in'):
                if not write_in_slots_allowed:
                    logging.info('Write-in not allowed.')
                    return False        # Write in not allowed
                elif candidate_ranking['rank']:
                    num_ranks_required += 1
                    write_in_slots_used += 1
                else:
                    logging.info('Write in was specified but not ranked')
                    return False        # Write in was specified but not ranked
                
    for verified in candidates_verified.values():
        if not verified: 
            logging.info('Not all candidates verified')
            return False   # Not all candidates verified
    ranks.sort()
    logging.info("Verifying ranks.")
    if len(ranks) == 0 and not required: return True
    if ranks[0] != 1 or ranks[len(ranks)-1] != num_ranks_required:
        logging.info(num_ranks_required)
        logging.info(ranks)
        logging.warning("Number of rankings don't match")
        return False    # Number of rankings don't match
    if write_in_slots_used > write_in_slots_allowed: 
        logging.warning("More write-in slots used than allowed")
        return False
    logging.info('Ballot for position %s verified.', election_position.position.name)
    return True

def cast_ranked_choice_ballot(position):
    """
    Records a ranked choice ballot in the models. Modifies write-in ids of the dictionary to reflect the 
    written-in candidate's id.
    
    Args:
        position{dictionary}: the verified position dictionary from the client
    """
    election_position = models.RankedVotingPosition.get(position['id'])
    preferences = [None] * len(position['candidate_rankings'])
    for cr in position['candidate_rankings']:
        
        # Check for a write-in
        if cr['id'].startswith('write-in'):
            epc = models.ElectionPositionCandidate.gql('WHERE election_position=:1 AND name=:2',
                                                         election_position, cr['name']).get()
            if not epc:
                epc = models.ElectionPositionCandidate(election_position=election_position,
                                                         net_id=None,
                                                         name=cr['name'],
                                                         written_in=True)
                epc.put()
            cr['id'] = str(epc.key())
        rank = cr['rank']
        preferences[rank-1] = models.ElectionPositionCandidate.get(cr['id']).key()
    
    logging.info(preferences)
    assert None not in preferences
    ballot = models.RankedBallot(position=election_position,
                                   preferences=preferences)
    ballot.put()
    logging.info('Stored ballot in database with preferences %s', preferences)

def verify_cumulative_voting_ballot(position):
    """
    Verifies the validity a cumulative voting ballot.
    
    Args:
        position{dictionary}: the position dictionary from the client
    
    Returns:
        True if valid, False if invalid. None if empty ballot.
    """
    logging.info('Verifying cumulative choice ballot.')
    election_position = models.CumulativeVotingPosition.get(
        position['id'])
    if not election_position:
        logging.warning('No election position found in models.')
        return False
    assert election_position.position_type == 'Cumulative-Voting'

    required = election_position.vote_required
    election_position_candidates = models.ElectionPositionCandidate.gql(
        'WHERE election_position=:1 AND written_in=False',
        election_position)
    write_in_slots_allowed = election_position.write_in_slots
    write_in_slots_used = 0
    points_required = election_position.points
    points_used = 0
    verified_candidates = {}
    for epc in election_position_candidates:
        verified_candidates[str(epc.key())] = True
    for cp in position['candidate_points']:
        if cp['points'] < 0:
            logging.warning("Negative points not allowed")
            return False   # Negative points not allowed
        points_used += cp['points']
        verified_candidates[cp['id']] = True
        if cp['id'].startswith('write-in-'):
            if not write_in_slots_allowed:
                logging.warning('Write-in not allowed.')
                return False
            elif cp['name'] and not cp['points']:
                logging.warning('Write-in was specified but not ranked.')
                return False
            elif cp['name'] and cp['points']:
                write_in_slots_used += 1
        else:
            if cp['id'] not in verified_candidates:
                logging.warning('Unknown')

    if write_in_slots_used > write_in_slots_allowed: return False
    if points_used == 0: return None
    if points_used != points_required: return False
    logging.info('Ballot for position %s verified.',
                 election_position.position.name)
    return True

def cast_cumulative_voting_ballot(position):
    """
    Records a cumulative choice ballot in the models. Modifies write-in
    ids of the dictionary to reflect the written-in candidate's id.

    Args:
        position{dictionary}: the verified position dictionary from client
    """
    election_position = models.CumulativeVotingPosition.get(position['id'])
    ballot = models.CumulativeVotingBallot(position=election_position)
    ballot.put()
    for cp in position['candidate_points']:
        if cp['points'] > 0:
            # Check for a write-in
            if cp['id'].startswith('write-in'):
                epc = models.ElectionPositionCandidate.gql('WHERE election_position=:1 AND name=:2',
                                                             election_position,
                                                             cp['name']).get()
                if not epc:
                    epc = models.ElectionPositionCandidate(election_position=election_position,
                                                             net_id=None,
                                                             name=cp['name'],
                                                             written_in=True)
                    epc.put()
                cp['id'] = str(epc.key())
            epc = models.ElectionPositionCandidate.get(cp['id'])
            choice = models.CumulativeVotingChoice(ballot=ballot,
                                                     candidate=epc,
                                                     points=cp['points'])
            choice.put()
    logging.info('Stored cumulative choice ballot in models.')

"""
Main router for request urls.
"""

__author__ = 'Waseem Ahmad <waseem@rice.edu>'

import webapp2


DEV_MODE = True


from models.admin_.organization import OrganizationPanelHandler
from models.admin_.organization_.election import ElectionPanelHandler
from models.admin_.organization_.election_.information import ElectionInformationHandler
from models.admin_.organization_.election_.positions import ElectionPositionsHandler
from models.admin_.organization_.election_.voters import ElectionVotersHandler
admin = webapp2.WSGIApplication([
    ('/admin/organization', OrganizationPanelHandler),
    ('/admin/organization/election', ElectionPanelHandler),
    ('/admin/organization/election/information', ElectionInformationHandler),
    ('/admin/organization/election/positions', ElectionPositionsHandler),
    ('/admin/organization/election/voters', ElectionVotersHandler),
    ('/admin/organization/election/.*', ElectionPanelHandler)
], debug=DEV_MODE)


import controllers.authenticate as _auth
authenticate = webapp2.WSGIApplication([
    ('/authenticate/login-response', _auth.LoginResponseHandler),
    ('/authenticate/logout', _auth.LogoutHandler),
    ('/authenticate/logout-response', _auth.LogoutResponseHandler),
    ('/authenticate/cleanup-sessions', _auth.CleanupSessionsHandler)
], debug=DEV_MODE)


import controllers.vote as _vote
vote = webapp2.WSGIApplication([
    ('/vote', _vote.VoteHandler),
    ('/vote/cast-ballot', _vote.BallotHandler),
    ('/vote/view-results', _vote.ResultsHandler)
], debug=DEV_MODE)


from models.admin_.organization_.election_.information import ElectionTaskHandler
from models.admin_.organization_.election_.voters import ElectionVotersTaskHandler
tasks = webapp2.WSGIApplication([
    ('/tasks/admin/organization/election/information', ElectionTaskHandler),
    ('/tasks/admin/organization/election/voters', ElectionVotersTaskHandler)
], debug=DEV_MODE)


import controllers.main as _main
main = webapp2.WSGIApplication([
    ('/stats/votes-count', _main.VotesCountHandler),
    ('/.*', _main.StaticHandler)
], debug=DEV_MODE)
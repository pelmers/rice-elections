"""
Run once, be happy forever. (Only once!)
If this ends up on Github...
"""

from models import models


def create_not_supported_universities():
  print "Creating not supported universities..."
  universities = open('data/top500universities.txt', 'r').readlines()
  for uni_name in universities:
    models.NotSupportedUniversity(name=uni_name.strip()).put()
    print "\tCreated %s" % uni_name.strip()

def create_supported_universities():
  print "Creating supported universities..."
  universities = [
    {'name': 'Rice University',
     'cas_server': 'https://netid.rice.edu'},
    {'name': 'Columbia University',
     'cas_server': 'https://cas.columbia.edu'},
    {'name': 'Princeton University',
     'cas_server': 'https://fed.princeton.edu'}
  ]
  for uni in universities:
    models.CASUniversity(name=uni['name'], cas_server=uni['cas_server']).put()
    print "\tCreated %s" % uni['name']
    not_supported = models.NotSupportedUniversity.gql(
                                            "WHERE name=:1", uni['name']).get()
    if not_supported:
      not_supported.delete()
      print "\tDeleted %s from not supported universities." % uni['name']

def main():
  print "Running setup script..."
  create_not_supported_universities()
  create_supported_universities()
  print "Done."

if __name__ == '__main__':
  main()
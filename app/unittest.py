import main
import simplejson as json
import logging
import os

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users


class TestHandler(webapp.RequestHandler):
      def get(self):
          logging.debug('Running unit tests')
          self.testEntityCD()
      def testEntityCD(self):      
            logging.debug('Testing entity create & delete...')
            sponsor = main.Sponsor()
            sponsor.name='Test Sponsor'
            sponsor.url= 'http://www.redcross.com'
            sponsor.address= '123 blaj blah, blah WA,USA'
            sponsor.phone= '(555)555-555'
            sponsor.put()
            assert sponsor.key()

            test_client = main.Client()
            test_client.displayName = "Bob"
            test_client.fullName = "Bob the builder"
            test_client.story  = "story"*256
            test_client.sponsor  = db.get(sponsor.key())
            test_client.imageURL = "http://www.test.org/img.png"
            test_client.shortCode = "12345"
            test_client.put()
            assert test_client.key()

            test_donor = main.Donor()
            test_donor.address="123 123 123"
            test_donor.name ="Donor"
            test_donor.phone = "(206)555-5555"
            test_donor.put()
            assert test_donor.key()
      
            test_user = main.User()
            test_user.user = users.get_current_user()
            test_user.isAdmin = True
            test_user.sponsor = db.get(sponsor.key())
            test_user.put()
            assert test_user.key()
            
            tx = main.Transaction()
            fromAccount = 'stripe'
            toAccount = '%s/%s'%(sponsor.key(),test_client.key())
            amount = 1.00
            type = 'CREDIT'
            note = 'A DONATion From Bob'
            confirm = False
            tx.put()
            
            #clean up
            tx.delete()
            test_user.delete()
            test_client.delete()
            sponsor.delete()
            test_donor.delete()
            
            self.response.out.write("<html><body><p>Test Passed!</p></body></html>")
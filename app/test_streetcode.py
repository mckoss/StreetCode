import logging
import string
import random
import re

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users

import models
from rest import counter


class TestDataHandler(webapp.RequestHandler):
    def get(self):

        sponsor = models.Sponsor()
        sponsor.name = random_sentence(3).title()
        sponsor.url = 'http://www.redcross.com/'
        sponsor.address = '123 Streeet Ave. S, Blah WA,USA'
        sponsor.phone = '(555)555-555'
        sponsor.put()
        self.response.out.write("<p>Created  Sponsor:[%s] </p>" %
                                (sponsor.key().id_or_name()))
        for i in range(0, 5):
            test_client = models.Client()
            test_client.set_defaults()
            test_client.displayName = "Bob"
            test_client.fullName = "Bob " + random_sentence(1).title()
            test_client.story = '<p>' + random_sentence(100) + '</p>'
            test_client.sponsor = sponsor
            test_client.imageURL = "http://www.test.org/img%i.png" % i
            test_client.put()
            self.response.out.write("<p>Created Client:[%s]</p>" %
                                    test_client.key().id_or_name())


class TestHandler(webapp.RequestHandler):
    def get(self):
        logging.debug('Loading test data')
        self.testEntityCD()

    def testEntityCD(self):
        logging.debug('Testing entity create & delete...')
        sponsor = models.Sponsor()
        sponsor.name = 'Test Sponsor'
        sponsor.url = 'http://www.redcross.com'
        sponsor.address = '123 blaj blah, blah WA,USA'
        sponsor.phone = '(555)555-555'
        sponsor.put()
        assert sponsor.key()

        test_client = models.Client()
        test_client.set_defaults()
        test_client.displayName = "Bob"
        test_client.fullName = "Bob the builder"
        test_client.story = lorem_ipsum
        test_client.sponsor = sponsor
        test_client.imageURL = "http://www.test.org/img.png"
        test_client.put()
        assert test_client.key()

        test_donor = models.Donor()
        test_donor.address = "123 123 123"
        test_donor.name = "Donor"
        test_donor.phone = "(206)555-5555"
        test_donor.put()
        assert test_donor.key()

        test_user = models.User()
        test_user.user = users.get_current_user()
        test_user.isAdmin = True
        test_user.sponsor = sponsor
        test_user.put()
        assert test_user.key()

        tx = models.Transaction()
        fromAccount = 'stripe'
        toAccount = '%s/%s' % (sponsor.key(), test_client.key())
        amount = 1.00
        type = 'CREDIT'
        note = 'A donation from Bob'
        confirm = False
        tx.put()

        # clean up
        tx.delete()
        test_user.delete()
        test_client.delete()
        sponsor.delete()
        test_donor.delete()

        self.response.out.write("<html><body><p>Test Passed!</p></body></html>")

lorem_ipsum = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas tellus mi, scelerisque a pharetra sed, consectetur in odio. Sed consectetur imperdiet nisl. Ut et diam arcu. Nunc consequat aliquam orci in elementum. Morbi auctor luctus pharetra. Mauris non lacus lectus. Nullam at velit ipsum. Nunc mattis interdum orci, et tempor nisi fringilla sit amet. Proin at dictum tellus. Mauris et tortor gravida justo tempus posuere quis nec nisi. Nullam lacinia lobortis ante, vel posuere enim gravida sit amet. Etiam placerat, erat eget eleifend consequat, magna augue egestas felis, eget egestas neque orci sit amet neque. Quisque vitae urna lorem. In nec dolor leo, vel fringilla arcu. Mauris porta porta tristique.
"""

re_words = re.compile(r"\s*(?:\s|\.|,)+\s*")
lorem_words = re_words.split(lorem_ipsum)

def random_sentence(n=10):
    return ' '.join([random.choice(lorem_words) for x in range(n)])

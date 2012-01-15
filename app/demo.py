import main
import simplejson as json
import logging
import os
import random
import string

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users

def randomDigits(digits=10):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(digits))

class DemoDataHandler(webapp.RequestHandler):

      def __init__(self):
            self.sponsors = []
            self.clients = []
      def get(self):
          logging.info('Loading sample data...')
          self.loadSponsors()
          self.loadClients()
          client_ids = ' , '.join([x.shortCode for x in self.clients])
          self.response.out.write("<html><body><p>Demo Data Created</p>"+
                                  "<p>Created Client Short Codes: "+client_ids+
                                  "</p></body></html>")

      def loadClients(self):
          self.buildKodiac()


      def buildKodiac(self):
          kodiac = main.Client()
          kodiac.set_defaults()
          kodiac.shortCode = 'AB'
          kodiac.displayName = "Kodiak"
          kodiac.fullName = "Chris"
          kodiac.imageURL = "/images/clients/Kodiac.png"
          kodiac.sponsor = self.sponsors[0]

          kodiac_story= "<p>Meet Chris. His friends call him \"Kodiak\".</p>"
          kodiac_story+="<p>He has a bear of a personality and always hugs instead of shaking hands.  "
          kodiac_story+="Moved to Seattle this past fall, but have been unable to find a job or steady housing.  "
          kodiac_story+="He is currently living in a men's shelter that doesn't have a kitchen or any refrigeration. "
          kodiac_story+="<p>The food stamps he gets can only be used for dry foods - everything which he has to carry in his backpack.  "
          kodiac_story+="He wants a hot meal and a new winter coat.</p><p> You can help.</p>"

          kodiac.story=kodiac_story

          kodiac.put()
          self.clients.append(kodiac)

      def loadSponsors(self):
          logging.debug('Creating sponsors')
          bread = main.Sponsor()
          bread.name='Bread of Life Mission'
          bread.url= 'http://www.breadoflifemission.org'
          bread.address= '97 South Main Street  Seattle, WA 98104-2513'
          bread.phone= '(206) 682-3579'
          bread.put()
          self.sponsors.append(bread)



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
                                  "<p>Client Short Codes:"+client_ids+
                                  "</p></body></html>")
          
      def loadClients(self):
          james = main.Client()
          james.set_defaults()
          james.displayName = "James & Carter"
          james.fullName = "James"
          james.imageURL = "http://assest/img/clients/james.png"
          james.sponsor = self.sponsors[0]
          james.put()
          self.clients.append(james)
            
      def loadSponsors(self):
          logging.debug('Creating sponsors')
          bread = main.Sponsor()
          bread.name='Bread of Life Mission'
          bread.url= 'http://www.breadoflifemission.org'
          bread.address= '97 South Main Street  Seattle, WA 98104-2513'
          bread.phone= '(206) 682-3579'
          bread.put()
          self.sponsors.append(bread)
          
          

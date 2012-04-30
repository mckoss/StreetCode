import logging

from google.appengine.ext import webapp
import models


class DemoDataHandler(webapp.RequestHandler):
    def __init__(self):
        self.sponsors = []
        self.clients = []

    def get(self):
        logging.info('Loading sample data...')
        self.loadSponsors()
        self.loadClients()
        client_ids = ', '.join([x.shortCode for x in self.clients])
        self.response.out.write("<html><body><p>Demo Data Created</p>" +
                                "<p>Created Client Short Codes: " + client_ids +
                                "</p></body></html>")

    def loadClients(self):
        self.buildKodiac()

    def buildKodiac(self):
        kodiac = models.Client()
        kodiac.set_defaults()
        kodiac.shortCode = 'kodiak'
        kodiac.name = "Kodiak"
        kodiac.fullName = "Chris"
        kodiac.imageURL = "/images/clients/Kodiak.png"
        kodiac.sponsor = self.sponsors[0]

        kodiac.story = \
"""<p>Meet Chris. His friends call him \"Kodiak\".</p>
<p>He has a bear of a personality and always hugs instead of shaking hands.
Moved to Seattle this past fall, but have been unable to find a job or steady housing.
He is currently living in a men's shelter that doesn't have a kitchen or any refrigeration.
<p>The food stamps he gets can only be used for dry foods - everything which he has to carry in
his backpack.  He wants a hot meal and a new winter coat.</p><p> You can help.</p>
"""

        kodiac.put()
        self.clients.append(kodiac)

    def loadSponsors(self):
        logging.info('Creating sponsors')
        bread = models.Sponsor()
        bread.name = 'Bread of Life Mission'
        bread.url = 'http://www.breadoflifemission.org'
        bread.address = '97 South Main Street  Seattle, WA 98104-2513'
        bread.phone = '(206) 682-3579'
        bread.put()
        self.sponsors.append(bread)

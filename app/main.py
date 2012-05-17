from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import settings
import rest
import models
import views
import paypal

from rest.views import PageHandler

import test_streetcode
import demo


models.init()


paths = [
   ('/', views.RootHandler ),
    ]

paths.extend(rest.get_paths())

paths.extend([
    ('/(\w+)', PageHandler.using('mobile_profile.html')),
    ('/client/(\w+)/(\d+)', views.ClientHandler),
    ('/donations/(\w+)', PageHandler.using('mobile_donation.html')),
    ('/paypal/ipn', paypal.IPNHandler), # paypal ipn handler
    ('/paypal/pdt/(\w+)', paypal.PDTHandler), # paypal pdt handler
    ])

def main():
    application = webapp.WSGIApplication(paths, debug=True)
    run_wsgi_app(application)


if __name__ == '__main__':
    main()

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import settings
import rest
import models
import views
import paypal

from rest.views import get_template_handler

models.init()

import test_streetcode
import demo

paths = [
    ('/', get_template_handler('index.html')),
    ('/about', get_template_handler('about.html')),
    ('/contact', get_template_handler('contact.html')),
    ('/donation/(\w+)', paypal.pdt_handler), # paypal pdt handler
    ]

paths.extend(rest.get_paths())

# Lower priority than fixed and admin urls.
paths.extend([
    ('/(\w+)', get_template_handler('mobile_profile.html')),
    ('/client/(\w+)/(\d+)', views.ClientHandler),
    ('/paypal_endpoint/', paypal.ipn_handler), # paypal ipn handler
    ])


def main():
    application = webapp.WSGIApplication(paths, debug=True)
    run_wsgi_app(application)


if __name__ == '__main__':
    main()

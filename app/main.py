from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import settings
import rest
import models
import views

from rest.views import get_template_handler

models.init()

import test_streetcode
import demo

paths = [
    ('/', get_template_handler('index.html')),

    ('/1(\w+)', get_template_handler('mobile_profile.html')),
    ('/client/(\w+)/(\d+)', views.ClientHandler),
    ]

paths.extend(rest.get_paths())

# Testing URL's (should not be in production)
if settings.DEBUG:
    paths.extend([\
        ('/test/run', test_streetcode.TestHandler),
        ('/test/test-data', test_streetcode.TestDataHandler),
        ('/test/demo-data', demo.DemoDataHandler),
        ])


def main():
    application = webapp.WSGIApplication(paths, debug=True)
    run_wsgi_app(application)


if __name__ == '__main__':
    main()

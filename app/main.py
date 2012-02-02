#!/usr/bin/env python
from google.appengine.ext import webapp

import settings
import models
import views
import rest_views

import test_streetcode
import demo

paths = [
    ('/', views.MainHandler),

    ('/1(\w+)', views.ProfileHandler),
    ('/client/(\w+)/(\d+)', views.ClientHandler),

    # REST API requires two handlers - one with an ID and one without.
    ('/data/(\w+)', rest_views.ListHandler),
    ('/data/(\w+)/(\d+)', rest_views.ItemHandler),
    ]

# Testing URL's (should not be in production)
if settings.DEBUG:
    paths.append([\
        ('/test/run', test_streetcode.TestHandler),
        ('/test/test-data', test_streetcode.TestDataHandler),
        ('/test/demo-data', demo.DemoDataHandler),
        ])


def main():
    application = webapp.WSGIApplication([
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

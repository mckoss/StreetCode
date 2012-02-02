from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import settings
import user_views
import rest_views
import models
import views

import test_streetcode
import demo

paths = [
    ('/', user_views.MainHandler),

    ('/1(\w+)', views.ProfileHandler),
    ('/client/(\w+)/(\d+)', views.ClientHandler),

    # REST API requires two handlers - one with an ID and one without.
    ('/data/(\w+)', rest_views.ListHandler),
    ('/data/(\w+)/(\d+)', rest_views.ItemHandler),
    ]

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

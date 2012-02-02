from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template


class UserHandler(webapp.RequestHandler):
    """ This subclass of RequestHandler sets user and user_id
    variables to be used in processing the request. """
    def __init__(self, *args, **kwargs):
        super(UserHandler, self).__init__(*args, **kwargs)
        self.user = users.get_current_user()
        self.user_id = self.user and self.user.user_id() or 'anonymous'


class MainHandler(UserHandler):
    def get(self):
        username = self.user and self.user.nickname()
        self.response.out.write(template.render("index.html",
            {"sign_in": users.create_login_url('/'),
             "sign_out": users.create_logout_url('/'),
             "username": username,
             }))

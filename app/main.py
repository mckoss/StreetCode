#!/usr/bin/env python
import simplejson as json
import logging
import os
import unittest
import settings

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

from jsonmodel import JSONModel, json_response

#Data Models
class Sponsor(JSONModel):
    name= db.StringProperty()
    url= db.LinkProperty()
    address= db.PostalAddressProperty()
    phone= db.PhoneNumberProperty()
    
class Client(JSONModel):
    displayName = db.StringProperty()
    fullName = db.StringProperty()
    story  = db.TextProperty()
    sponsor  = db.ReferenceProperty(Sponsor)
    imageURL = db.LinkProperty()
    shortCode = db.StringProperty()

class Donor(JSONModel):
    name= db.StringProperty()
    address= db.PostalAddressProperty()
    phone= db.PhoneNumberProperty()
    
class User(JSONModel):
    isAdmin = db.BooleanProperty()
    sponsor = db.ReferenceProperty(Sponsor)
    user = db.StringProperty()#(app engine credentials)

class Transaction(JSONModel):
    fromAccount = db.LinkProperty()#(e.g., 'stripe')
    toAccount =db.LinkProperty() #(e.g. 'sponsor_id/client_id' like 'sponsor_64/client_12')
    amount = db.FloatProperty()
    type = db.StringProperty()
    note = db.TextProperty()
    confirm = db.BooleanProperty()
    
class Scan(JSONModel):
    client = db.ReferenceProperty(Sponsor)
    donor = db.ReferenceProperty(Donor)
    ledger = db.ReferenceProperty(Transaction)
    
#Handlers

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


class ProfileHandler(UserHandler):
    def get(self, id):
        self.response.out.write(template.render("templates/mobile_profile.html",
                                                {'id': id,
                                                 'SITE_NAME': settings.SITE_NAME}
                                                ))


class ListHandler(UserHandler):
    def get_model(self, model_name):
        if model_name not in handle_models:
            self.error(404)
            self.response.out.write("Model '%s' not in %r" % (model_name, handle_models))
            return None
        return handle_models[model_name]

    # get all list of items
    def get(self, model_name):
        model = self.get_model(model_name)
        if model is None:
            return
        query = model.all().filter('user_id =', self.user_id)
        items = [item.get_dict() for item in query.fetch(1000)]
        json_response(self.response, items)

    # create an item
    def post(self, model_name):
        model = self.get_model(model_name)
        if model is None:
            return
        data = json.loads(self.request.body)
        item = model(user_id=self.user_id)
        item.set_dict(data)
        item.put()
        json_response(self.response, item.get_dict())


# The Todo model handler - used to handle requests with
# a specific ID.
class ItemHandler(UserHandler):
    def get(self,model_name,id):
        item = self.get_item(model_name, id)
        if not item:
            return
        json_response(self.response, item.to_dict())
        
    def get_item(self, model_name, id):
        if model_name not in handle_models:
            self.error(404)
            return None
        model = handle_models[model_name]
        item = model.get_by_id(int(id))
        if item is None:
            self.error(404)
            return None
        return item

    def put(self, model_name, id):
        item = self.get_item(model_name, id)
        if not item:
            return

        data = json.loads(self.request.body)
        if item.user_id != self.user_id:
            self.error(403)
            self.response.out.write(json.dumps({
                'status': "Write permission failure."
                }))
            return

        item.set_dict(data)
        item.put()
        json_response(self.response, item.to_dict())

    def delete(self, model_name, id):
        item = self.get_item(model_name, id)
        if item:
            item.delete()


handle_models = {'client': Client,'donor':Donor,'sponsor':Sponsor,'scan':Scan,'transaction':Transaction}


def main():
    application = webapp.WSGIApplication([
        ('/', MainHandler),
        ('/go/(\w+)', ProfileHandler),

        # REST API requires two handlers - one with an ID and one without.
        ('/data/(\w+)', ListHandler),
        ('/data/(\w+)/(\d+)', ItemHandler),
        #unit test hamdler
        ('/test',unittest.TestHandler),
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

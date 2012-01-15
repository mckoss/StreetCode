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

class Accumulator(db.Model):
    counter = db.IntegerProperty(default=0)

    @classmethod
    def get_unique(cls):
        def increment_counter(key):
            obj = db.get(key)
            obj.counter += 1
            obj.put()
            return obj.counter

        acc = db.GqlQuery("SELECT * FROM Accumulator").get()
        if acc is None:
            acc = Accumulator()
            acc.put()
        return db.run_in_transaction(increment_counter, acc.key())


short_chars = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"

def int_to_sid(i):
    s = ''
    while i != 0:
        b = i % len(short_chars)
        s = short_chars[b] + s
        i = i / len(short_chars)
    return s

class Client(JSONModel):
    displayName = db.StringProperty()
    fullName = db.StringProperty()
    story  = db.TextProperty()
    sponsor  = db.ReferenceProperty(Sponsor)
    imageURL = db.LinkProperty()
    shortCode = db.StringProperty()

    def set_defaults(self):
        self.shortCode =int_to_sid(Accumulator.get_unique())


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


class ClientHandler(UserHandler):
    templates = {'card':'client_card.html','story':'client_story.html','sign':'sign.html'}
    def get(self,template_type,id):
        client_template = ClientHandler.templates[template_type]
        self.response.out.write(template.render("templates/%s"%client_template,
                                                {'id': id,
                                                 'SITE_NAME': settings.SITE_NAME}
                                                ))

class ProfileHandler(UserHandler):
    def get(self, id):
        self.response.out.write(template.render("templates/mobile_profile.html",
                                                {'id': id,
                                                 'SITE_NAME': settings.SITE_NAME}
                                                ))
class DesktopProfileHandler(UserHandler):
    def get(self, id):
        self.response.out.write(template.render("templates/desktop_profile.html",
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

        query = model.all()

        for property_name in self.request.arguments():
            paramValue = self.request.get(property_name)
            if '*' == paramValue[-1]:
                self.filter_query_by_prefix(query,model,property_name)
            else:
                self.filter_query_by(query,model,property_name)

        results = query.fetch(1000)
        logging.info("Found [%i] %s's"%(len(results),model_name))
        items = [item.get_dict() for item in results]
        json_response(self.response, items)

    def filter_query_by_prefix(self,query,model,property_name):
        prefix = str(self.request.get(property_name)[:-1])#don't include *
        logging.info("Prefix is %s"%prefix)
        last_char = chr(ord(prefix[-1])+1)
        query.filter("%s >= " % property_name, prefix).filter("%s < " % property_name, "%s%s"%(prefix,last_char))

    def filter_query_by(self,query,model,property_name):
        props = model.properties()
        value = props.get(property_name)
        paramValue = self.request.get(property_name)
        if isinstance(value, db.ReferenceProperty):
            ref_model = handle_models[property_name]
            ref_entity = ref_model.get_by_id(int(paramValue))
            query.filter('%s = '%property_name,ref_entity)
        else:
            query.filter('%s = '%property_name,paramValue)

    # create an item
    def post(self, model_name):
        model = self.get_model(model_name)
        if model is None:
            return

        # HACK
        if hasattr(model, 'set_defaults'):
            model.set_defaults()

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
        json_response(self.response, item.get_dict())

    def get_item(self, model_name, id):
        logging.info('args: %s'%self.request.arguments())
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

        ('/1(\w+)', ProfileHandler),
        ('/client/(\w+)/(\d+)', ClientHandler),
        # REST API requires two handlers - one with an ID and one without.
        ('/data/(\w+)', ListHandler),
        ('/data/(\w+)/(\d+)', ItemHandler),
        #load sample data
        ('/testdata',unittest.TestDataHandler),
        #unit test hamdler
        ('/test',unittest.TestHandler),
    ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

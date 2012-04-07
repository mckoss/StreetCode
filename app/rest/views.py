import os
import logging
import simplejson as json

from google.appengine.api import users
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template

import settings

import models
from models import json_response


class UserHandler(webapp.RequestHandler):
    """ This subclass of RequestHandler sets user and user_id
    variables to be used in processing the request. """
    def __init__(self, *args, **kwargs):
        super(UserHandler, self).__init__(*args, **kwargs)
        self.user = users.get_current_user()
        self.user_id = self.user and self.user.user_id() or 'anonymous'


class SchemaHandler(UserHandler):
    def get(self):
        results = {'schema': {}}
        for model_name, model in models.rest_models.items():
            results['schema'][model_name] = model.get_schema()
        json_response(self.response, results)


class ListHandler(UserHandler):
    def get_model(self, model_name):
        if model_name not in models.rest_models:
            self.error(404)
            self.response.out.write("Model '%s' not in %r" % (model_name, models.rest_models))
            return None
        return models.rest_models[model_name]

    # get all list of items
    def get(self, model_name):
        model = self.get_model(model_name)
        if model is None:
            return

        query = model.all()

        should_cache = True

        for property_name in self.request.arguments():
            value = self.request.get(property_name)
            if property_name == 'no-cache':
                should_cache = False
                continue
            if '*' == value[-1]:
                filter_query_by_prefix(query, model, property_name, value[:-1])
            else:
                filter_query_by_value(query, model, property_name, value)

        results = query.fetch(1000)
        logging.info("Found [%i] %s's" % (len(results), model_name))
        items = [item.get_dict() for item in results]
        json_response(self.response, items, cache=should_cache)

    # create an item
    def post(self, model_name):
        model = self.get_model(model_name)
        if model is None:
            return

        # HACK - How else to initialize properties ONLY in the case
        # where a model is being created.
        data = json.loads(self.request.body)
        item = model(user_id=self.user_id)

        if hasattr(item, 'set_defaults'):
            item.set_defaults()

        item.set_dict(data)
        item.put()
        json_response(self.response, item.get_dict())


class ItemHandler(UserHandler):
    def get(self, model_name, id):
        item = self.get_item(model_name, id)
        if not item:
            return
        json_response(self.response, item.get_dict())

    def get_item(self, model_name, id):
        logging.info('args: %s' % self.request.arguments())
        if model_name not in models.rest_models:
            self.error(404)
            return None
        model = models.rest_models[model_name]
        item = model.get_by_id(int(id))
        if item is None:
            self.error(404)
            return None
        return item

    def put(self, model_name, id):
        logging.info("called put")
        item = self.get_item(model_name, id)
        if not item:
            return

        data = json.loads(self.request.body)
        if hasattr(item, 'user_id') and item.user_id != self.user_id:
            self.error(403)
            self.response.out.write(json.dumps({
                'status': "Write permission failure."
                }))
            return

        item.set_dict(data)
        item.put()
        json_response(self.response, item.get_dict())

    def delete(self, model_name, id):
        item = self.get_item(model_name, id)
        if item:
            item.delete()


def filter_query_by_prefix(query, model, property_name, prefix):
    last_char = chr(ord(prefix[-1]) + 1)
    logging.info("Prefix filter: '%s' <= %s < '%s'" %
                 (prefix, property_name, prefix[:-1] + last_char))
    query.filter('%s >= ' % property_name, prefix)
    query.filter('%s < ' % property_name, prefix[:-1] + last_char)


def filter_query_by_value(query, model, property_name, value):
    property = model.properties().get(property_name)
    # Get Key() to referenced object for filtering
    if isinstance(property, db.ReferenceProperty):
        kind = property.reference_class.kind()
        value = db.Key.from_path(kind, long(value))

    query.filter('%s = ' % property_name, value)


class PageHandler(UserHandler):
    def __init__(self, template_path, render_data=None):
        super(PageHandler, self).__init__()
        self.template_path = template_path
        self.render_data = render_data or {}

    def prepare(self):
        username = self.user and self.user.nickname()
        self.render_data.update({
                "sign_in": users.create_login_url('/'),
                "sign_out": users.create_logout_url('/'),
                "username": username,
                "site_name": settings.SITE_NAME,
                })

    def get(self, *args):
        self.prepare()
        logging.info("Rendering template: %s" % self.template_path)
        result = template.render(self.template_path, self.render_data)
        self.response.out.write(result)


def get_template_handler(template_name, render_data=None, package=None):
    def get_handler():
        path = ['templates', template_name]
        if package is not None:
            path.insert(0, package)
        return PageHandler(os.path.join(*path))
    return get_handler

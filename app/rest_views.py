import logging

from google.appengine.ext import db

from user_views import UserHandler
from models import rest_models
from jsonmodel import json_response


class ListHandler(UserHandler):
    def get_model(self, model_name):
        if model_name not in rest_models:
            self.error(404)
            self.response.out.write("Model '%s' not in %r" % (model_name, rest_models))
            return None
        return rest_models[model_name]

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
            ref_model = rest_models[property_name]
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


class ItemHandler(UserHandler):
    def get(self,model_name,id):
        item = self.get_item(model_name, id)
        if not item:
            return
        json_response(self.response, item.get_dict())

    def get_item(self, model_name, id):
        logging.info('args: %s'%self.request.arguments())
        if model_name not in rest_models:
            self.error(404)
            return None
        model = rest_models[model_name]
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

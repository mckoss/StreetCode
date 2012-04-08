from datetime import datetime
import time
import logging
import simplejson as json

from google.appengine.ext import db
from google.appengine.api.datastore_errors import *
from google.appengine.api.datastore_types import Text


JSON_MIMETYPE = 'application/json'
JSON_MIMETYPE_CS = JSON_MIMETYPE + '; charset=utf-8'

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list, Text)
JS_TYPES = ('number', 'number', 'number', 'boolean', 'object', 'string', 'object', 'string')

# TODO: Sloppy - should traverse, stopping at cycles
DEPTH_MAX = 5

rest_models = {}


def add_model(name, model):
    """ Add a model class. """
    logging.info("Initializing model: %s" % name)
    rest_models[name] = model


def add_models(model_list):
    """ Add all the models defined in the module. """
    for name, model in model_list.items():
        add_model(name, model)


class RESTModel(db.Model):
    # Every model has a name property - used to display in lists.
    name = db.StringProperty()

    def set_defaults(self):
        pass

    """ Conversion of model to and from JSON for REST interface. """
    @classmethod
    def get_schema(self):
        result = {'properties': {}}

        if hasattr(self, 'form_order'):
            result['formOrder'] = self.form_order

        if hasattr(self, 'computed'):
            result['computed'] = self.computed

        for prop_name, property in self.properties().items():
            result['properties'][prop_name] = py_to_js_type(property.data_type)
        return result

    def get_dict(self, depth=1):
        result = {'id': self.key().id_or_name()}

        for prop_name, property in self.properties().iteritems():
            try:
                value = getattr(self, prop_name)
            except ReferencePropertyResolveError, e:
                # Might not be safe to grab this 'decorated' attribute
                # name in order to read the raw key from a ReferenceProperty.
                # http://code.google.com/p/googleappengine/issues/detail?id=991
                # key = getattr(self, '_' + prop_name)
                key = self.get_value_for_datastore(self)
                value = {'status': 'deleted', 'id': key.id_or_name()}

            if value is None or isinstance(value, SIMPLE_TYPES):
                result[prop_name] = value
            elif isinstance(value, datetime):
                ms = time.mktime(value.utctimetuple()) * 1000
                ms += getattr(value, 'microseconds', 0) / 1000
                result[prop_name] = int(ms)
            elif isinstance(value, db.GeoPt):
                result[prop_name] = {'lat': value.lat, 'lon': value.lon}
            elif isinstance(value, db.Model):
                if depth == DEPTH_MAX:
                    result[prop_name] = {'status': 'depth/max'}
                else:
                    result[prop_name] = value.get_dict(depth + 1)
            else:
                raise ValueError('cannot encode ' + repr(prop))

        return result

    def set_dict(self, json_dict):
        for prop_name, prop in self.properties().iteritems():
            if prop_name not in json_dict:
                continue

            value = json_dict[prop_name]

            if value is None or prop.data_type in SIMPLE_TYPES:
                pass
            elif prop.data_type == datetime:
                value = datetime.utcfromtimestamp(value / 1000)
                value.microseconds = (value % 1000) * 1000
            elif prop.data_type == db.GeoPt:
                value = db.GeoPt(value.lat, value.lon)
            elif prop.data_type in rest_models.values():
                value = db.Key.from_path(prop.data_type.kind(), value)
            else:
                raise ValueError('cannot decode %s: %r (type %s)' % (prop_name,
                                                                     value,
                                                                     prop.data_type))

            setattr(self, prop_name, value)

    def from_json(self, json_string):
        self.set_dict(json.loads(json_string))


class Timestamped(db.Model):
    """
    Standardized timestamp information for models.
    """
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty()

    read_only = ('created', 'modified')

    def put(self, *args, **kwargs):
        # Don't rely on auto_now property to set the modification
        # time since it does not seem to be over-written in the model
        # after a put().
        self.modified = datetime.now()
        super(Timestamped, self).put(*args, **kwargs)


class ModelEncoder(json.JSONEncoder):
    """
    Encode some common datastore property types to JSON.
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            # Convert date/datetime to ms-since-epoch ("new Date()").
            ms = time.mktime(value.utctimetuple()) * 1000
            ms += getattr(value, 'microseconds', 0) / 1000
            return int(ms)
        return json.JSONEncoder.default(self, obj)


def pretty_json(json_dict):
    return json.dumps(json_dict, sort_keys=True, indent=2,
                      separators=(',', ': '), cls=ModelEncoder)


def json_response(response, json_dict, cache=False):
    response.headers['Content-Type'] = JSON_MIMETYPE_CS
    if cache:
        response.headers['Cache-Control'] = 'max-age=3600'
    response.out.write(pretty_json(json_dict))


def py_to_js_type(py_type):
    """ Return { "type": "<JavaScript data type>", "control": "<HTML input type>" } """
    # TODO: Add Model Reference Type

    result = {'control': 'text'}
    if py_type in SIMPLE_TYPES:
        i = list(SIMPLE_TYPES).index(py_type)
        result['type'] = JS_TYPES[i]
    if py_type == datetime:
        result['type'] = 'Date'
    if py_type == db.GeoPt:
        result['type'] = 'GeoPt'
    if py_type == Text:
        result['control'] = 'textarea'
    if py_type in rest_models.values():
        i = rest_models.values().index(py_type)
        result['control'] = 'reference';
        result['type'] = rest_models.keys()[i]
    if 'type' not in result:
        result['type'] = '%r' % py_type
    return result

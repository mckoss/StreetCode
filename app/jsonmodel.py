from datetime import datetime
import time
import logging
import simplejson as json

from google.appengine.ext import db
from google.appengine.api.datastore_errors import *


JSON_MIMETYPE = 'application/json'
JSON_MIMETYPE_CS = JSON_MIMETYPE + '; charset=utf-8'

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)

# TODO: Sloppy - should traverse, stopping at cycles
DEPTH_MAX = 5


class JSONModel(db.Model):
    """ Conversion of model to and from JSON """
    def get_dict(self, depth=1):
        result = {'id': self.key().id_or_name()}

        for prop_name, property in self.properties().iteritems():
            try:
                value = getattr(self, prop_name)
            except ReferencePropertyResolveError, e:
                # Might not be safe to grab this 'decorated' attribute
                # name in order to read the raw key from a ReferenceProperty.
                # http://code.google.com/p/googleappengine/issues/detail?id=991
                key = getattr(self, '_' + prop_name)
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
            elif prop.date_type == datetime:
                value = datetime.utcfromtimestamp(value / 1000)
                value.microseconds = (value % 1000) * 1000
            elif prop.date_type == db.GeoPt:
                value = db.GeoPt(value.lat, value.lon)
            elif isinstance(value, db.Model):
                raise ValueError('NYI: reading model keys: %s' % value.kind())
            else:
                raise ValueError('cannot decode: %r ', value)

            setattr(self, prop_name, value)

    def from_json(self, json_string):
        self.set_dict(json.loads(json_string))


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


def json_response(response, json_dict):
    response.headers['Content-Type'] = JSON_MIMETYPE_CS
    response.out.write(pretty_json(json_dict))

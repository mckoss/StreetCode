"""
    StreetCodes - appliction models/REST interface.
"""
from google.appengine.ext import db

import settings
import rest.models
from rest.models import RESTModel, Timestamped
import rest.counter as counter


def init():
    rest.models.add_models({
            'user': User,
            'sponsor': Sponsor,
            'client': Client,
            'donor': Donor,
            'transaction': Transaction,
            'scan': Scan,
            })


class Sponsor(RESTModel):
    url = db.StringProperty()
    address = db.TextProperty()
    phone = db.StringProperty()


class User(RESTModel):
    user = db.UserProperty()
    isAdmin = db.BooleanProperty()
    sponsor = db.ReferenceProperty(Sponsor)


class Client(RESTModel):
    fullName = db.StringProperty()
    story = db.TextProperty()
    sponsor = db.ReferenceProperty(Sponsor)
    imageURL = db.StringProperty()
    shortCode = db.StringProperty()


class Donor(RESTModel):
    address = db.TextProperty()
    phone = db.StringProperty()


class Transaction(RESTModel):
    """
    Simple double-entry accounting.  Account names are in the format:

        'type_id/type_id'

    for example:
        'stripe'
        'sponsor_34/client_2'

    type is one of 'donation', 'fullfillment', ...
    """
    fromAccount = db.StringProperty()
    toAccount = db.StringProperty()
    amount = db.FloatProperty()
    type = db.StringProperty()
    note = db.TextProperty()
    confirm = db.BooleanProperty()


class Scan(RESTModel):
    client = db.ReferenceProperty(Sponsor)
    donor = db.ReferenceProperty(Donor)
    ledger = db.ReferenceProperty(Transaction)

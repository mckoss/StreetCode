"""
    StreetCodes - appliction models/REST interface.
"""
from google.appengine.ext import db

import settings
from jsonmodel import JSONModel
import counter

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
    imageURL = db.StringProperty()
    shortCode = db.StringProperty()

    def set_defaults(self):
        self.shortCode = counter.int_to_sid(counter.Accumulator.get_unique())


class Donor(JSONModel):
    name= db.StringProperty()
    address= db.PostalAddressProperty()
    phone= db.PhoneNumberProperty()


class User(JSONModel):
    user = db.UserProperty()
    isAdmin = db.BooleanProperty()
    sponsor = db.ReferenceProperty(Sponsor)


class Transaction(JSONModel):
    """
    Simple double-entry accounting.  Account names are in the format:

        'type_id/type_id'

    for example:
        'stripe'
        'sponsor_34/client_2'

    type is one of 'donation', 'fullfillment', ...
    """
    fromAccount = db.LinkProperty()
    toAccount =db.LinkProperty()
    amount = db.FloatProperty()
    type = db.StringProperty()
    note = db.TextProperty()
    confirm = db.BooleanProperty()


class Scan(JSONModel):
    client = db.ReferenceProperty(Sponsor)
    donor = db.ReferenceProperty(Donor)
    ledger = db.ReferenceProperty(Transaction)


rest_models = {'client': Client,
               'donor': Donor,
               'sponsor': Sponsor,
               'scan': Scan,
               'transaction': Transaction,
               }

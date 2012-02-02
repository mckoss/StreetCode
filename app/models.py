"""
    StreetCodes - appliction models/REST interface.
"""
import settings

from google.appengine.ext import db
from jsonmodel import JSONModel, json_response

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


handle_models = {'client': Client,
                 'donor': Donor,
                 'sponsor': Sponsor,
                 'scan':Scan,
                 'transaction':Transaction
                 }

"""
    StreetCodes - appliction models/REST interface.

    Note that all models will inherit a default name (StringProperty).
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
            'paypal': PaypalMerchant,
            })

class PaypalMerchant(RESTModel, Timestamped):
    merchantEmail = db.StringProperty()  
    merchantKey = db.StringProperty()
    PDTKey = db.StringProperty() 

    form_order = ('name', 'merchantEmail', 'merchantKey', 'PDTKey')


class Sponsor(RESTModel, Timestamped):
    url = db.StringProperty()
    address = db.TextProperty()
    phone = db.StringProperty()
    paypalMerchant = db.ReferenceProperty(PaypalMerchant)

    form_order = ('name', 'url', 'address', 'phone', 'paypalMerchant')


class User(RESTModel, Timestamped):
    user = db.UserProperty()
    isAdmin = db.BooleanProperty()
    sponsor = db.ReferenceProperty(Sponsor)


class Client(RESTModel, Timestamped):
    fullName = db.StringProperty()
    shortCode = db.StringProperty()
    story = db.TextProperty()
    storyHTML = db.TextProperty()
    sponsor = db.ReferenceProperty(Sponsor)
    imageURL = db.StringProperty()

    form_order = ('name', 'fullName',
                  'shortCode',
                  'story', 'sponsor', 'imageURL',
                  'QRCode("http://streetcode.me/" + item.shortCode)',
                  )
    computed = ('item.storyHTML = markdown(item.story);',
                'item.shortCode = item.shortCode.toLowerCase();',
                )


class Donor(RESTModel, Timestamped):
    email = db.StringProperty()

    form_order = ('name', 'email')


class Transaction(RESTModel, Timestamped):
    donor = db.ReferenceProperty(Donor)
    client = db.ReferenceProperty(Client)
    txID = db.StringProperty() 
    method = db.StringProperty()
    paymentDate = db.StringProperty()
    amount = db.FloatProperty()
    fee = db.FloatProperty()
    paymentStatus = db.StringProperty()
    note = db.TextProperty()
    fulfilled = db.BooleanProperty(default=False)

    form_order = ('donor', 'client', 'txID', 'method', 'paymentDate',
        'amount', 'fee', 'paymentStatus', 'note', 'fulfilled')

class Scan(RESTModel, Timestamped):
    client = db.ReferenceProperty(Sponsor)
    donor = db.ReferenceProperty(Donor)
    ledger = db.ReferenceProperty(Transaction)

    form_order = ('name', 'client', 'donor', 'ledger')


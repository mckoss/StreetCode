import urllib
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
import re
import settings
from models import Transaction
from models import Client
from models import Donor

class DB(): 
    def getClient(self, shortCode, createNew = False):
        return Client.all().filter('shortCode =', shortCode).get()

    def getDonor(self, email):
        return Donor.all().filter('email', email).get()

    def createDonor(self, props): 
        donor = Donor()
        donor.name = "%s %s" % (props['first_name'], props['last_name'])
        donor.email = urllib.unquote( props['payer_email'] )
        donor.put()
        return donor 

    def getTransaction(self, trans_id ):
        return Transaction.all().filter('txID', trans_id).get()

    def createTransaction(self, props): 
        tx = Transaction( method = 'PayPal',
                      donor = props['donor'],
                      client = props['client'],
                      txID = props['trans_id'],
                      paymentDate = urllib.unquote(props['payment_date']).replace('+', ' '),
                      amount = float(props['payment_gross']),
                      fee = float(props['payment_fee']) ,
                      paymentStatus = props['payment_status'],
                      note = urllib.unquote(props['item_name']).replace('+', ' '),
                      fulfilled = False
                    )
        tx.put() 
        return tx


class PDTHandler(webapp.RequestHandler):
    def __init__(self):
        self.db = DB() 
        self.props = {
                'trans_id'  : '',
                'sponsor'   : '',
                'client'    : '',
                'merchant'  : '',
                'payment_date'  : '',
                'payment_gross' : 0,
                'payment_fee'   : 0,
                'payment_status': '',
                'item_name' : '',
                'first_name': '',
                'last_name' : '',
                'payer_email'   : '' }

     # build a dictionary of key value pair provided by PDT
    def parsePaypalStatus (self, status ):
        lines = status.split( '\n' )
        
        for line in lines[1:] :
            items = line.split('=')
            if len(items) == 2:
                key, value = items
                self.props[key] = value
            else:
                self.props[key] = ''

    def get(self, shortCode):
        # Get client by shortCode to get access to corresponding merchant PDT key
        client = self.db.getClient(shortCode) 
        if client is None: 
            return
        
        self.props['client'] = client.sponsor
        self.props['sponsor'] = client.sponsor.paypalMerchant
        self.props['merchant'] = merchant

        # First get the Paypal transaction ID and verify that the transaction is successful        
        trans_id = self.request.get("tx")
        self.props['trans_id'] = trans_id

        # Confgure POST args for Paypal
        args = {
            "cmd"   : "_notify-synch",
            "tx"    : trans_id,
            "at"    : merchant.PDTKey
        }
        args = urllib.urlencode(args)

        try:
            # Do a post back to validate the transaction data
            status = urlfetch.fetch(url     = settings.PAYPAL_URL,
                                    method  = urlfetch.POST,
                                    payload = args).content
        except:
            self.response.out.write("Request for Paypal transaction data failed.")

        # If the transaction is successful, save the transaction data in the datastore
        if re.search("^SUCCESS", status):
            self.parsePaypalStatus( status )

            if self.props["payment_status"] == "Completed":
                # Get donor information (create new if object does not exist)
                donor = self.db.getDonor( urllib.unquote(self.props['payer_email']) )
                if donor is None: 
                    self.createDonor( self.props )
                self.props['donor'] = donor

                # Create a new transaction (use transaction_id to maintain data uniqueness)
                tx = self.db.getTransaction( trans_id )
                if tx is None: 
                    self.db.createTransaction( self.props )

            # Regardless of success of saving transaction, the user is redirected to thank you screen 
            self.redirect("/"+shortCode +"#thanks");
        else:
            self.response.out.write("Sorry, your Paypal transaction did not go through successfully.")

# class IPNHandler(webapp.RequestHandler):
#     def get (self, shortCode ):


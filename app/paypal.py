import urllib
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
import re
import settings
from models import Transaction
from models import Client
from models import Donor 
import traceback

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

    def getTransaction(self, txId ):
        return Transaction.all().filter('txID', txId).get()

    def createTransaction(self, props): 
        tx = Transaction( method = 'PayPal',
                      donor = props['donor'],
                      client = props['client'],
                      txID = props['txn_id'],
                      paymentDate = urllib.unquote(props['payment_date']).replace('+', ' '),
                      amount = float(props['mc_gross']),
                      fee = float(props['mc_fee']) ,
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
                'txn_id'  : '',
                'client'    : '',
                'payment_date'  : '',
                'payment_gross' : 0,
                'payment_fee'   : 0,
                'payment_status': '',
                'item_name' : '',
                'first_name': '',
                'last_name' : '',
                'payer_email'   : '' }

     # build a dictionary of key value pair provided by PDT
    def parsePDTMsg (self, status ):
        lines = status.split( '\n' )
        
        for line in lines[1:] :
            items = line.split('=')
            if len(items) == 2:
                key, value = items
                self.props[key] = value
            else:
                self.props[key] = ''

    def get(self):
        # Get client by shortCode to get access to corresponding merchant PDT key
        shortCode = self.request.get('cm')
        client = self.db.getClient(shortCode) 
        if client is None: 
            return
        
        self.props['client'] = client
        merchant = client.sponsor.paypalMerchant

        # First get the Paypal transaction ID and verify that the transaction is successful        
        txnId = self.request.get("tx")
        self.props['txn_id'] = txnId 

        # Confgure POST args for Paypal
        args = {
            "cmd"   : "_notify-synch",
            "tx"    : txnId,
            "at"    : merchant.PDTKey
        }
        args = urllib.urlencode(args)

        try:
            # Do a post back to validate the transaction data
            status = urlfetch.fetch(url     = settings.PAYPAL_URL,
                                    method  = urlfetch.POST,
                                    payload = args).content
            # If the transaction is successful, save the transaction data in the datastore
            if re.search("^SUCCESS", status):
                self.parsePDTMsg( status )

                # Get donor information (create new if object does not exist)
                donor = self.db.getDonor( urllib.unquote(self.props['payer_email']) )
                if donor is None: 
                    self.createDonor( self.props )
                self.props['donor'] = donor

                # Create a new transaction (use transaction_id to maintain data uniqueness)
                tx = self.db.getTransaction( txnId )
                if tx is None: 
                    self.db.createTransaction( self.props )

                # Regardless of success of saving transaction, the user is redirected to thank you screen 
                self.redirect("/" + shortCode + "#thanks");
            else:
                self.response.out.write("Sorry, your Paypal transaction did not go through successfully.<br>")
                self.response.out.write("Please contact Paypal to resolve any problems.")
        except:
            self.response.out.write("Request for Paypal transaction data failed.")
            return 

class IPNHandler(webapp.RequestHandler):
    def __init__ (self):
        self.db = DB() 
        self.props = {
                'txn_id'        : '',
                'client'        : '',
                'payment_date'  : '',
                'payment_gross' : 0,
                'payment_fee'   : 0,
                'payment_status': '',
                'item_name'     : '',
                'first_name'    : '',
                'last_name'     : '',
                'payer_email'   : '' }

    def verifyMerchant(self, merchant):
        return self.props['receiver_email'] != merchant.merchantEmail or self.props['receiver_id'] != merchant.merchantKey 

    def get (self) :
        if settings.DEBUG:
            self.post()
        else:
            self.redirect("/")

    def post (self ):
        # build a dictionary using POST data
        self.props["cmd"] = "_notify-validate"
        for arg in self.request.arguments(): 
            self.props[arg] = self.request.get(arg)

        
        # Get transaction ID, and IPN message type
        txnType = self.props["txn_type"]
        txnId = self.props["txn_id"]
        shortCode = self.props["custom"]


        # Handles payments only 
        if txnType == "web_accept" or txnType == "express_checkout" :
            try: 
                verifyStatus = urlfetch.fetch(  url = settings.PAYPAL_URL,
                                                method = urlfetch.POST,
                                                payload = urllib.urlencode(self.props) ).content

                if verifyStatus == "VERIFIED" : 
                    # Get the client by short Code this IPN is relevant 
                    client = self.db.getClient(shortCode) 
                    if client is None: 
                        return
                    self.props['client'] = client 

                    # if not verifyMerchant(client.sponsor.paypalMerchant): 
                    #   return 

                    # See if the transaction already exists
                    tx = self.db.getTransaction( txnId ) 
                    if tx is None: 
                        # If no transaction, create the donor and transaction in the datastore
                        donor = self.db.getDonor( urllib.unquote(self.props['payer_email']) )
                        if donor is None: 
                            donor = self.db.createDonor( self.props )
                        self.props['donor'] = donor
                        
                        tx = self.db.createTransaction(self.props)
                    else: 
                        # Update payment status for existing transaction 
                        tx.paymentStatus = self.props['payment_status']
                        tx.put()
            except:
                self.response.out.write("IPN message verification failed with the following error <br>") 
                self.response.out.write(traceback.format_exc())
                return
                    
                # TODO notify app admin of error 
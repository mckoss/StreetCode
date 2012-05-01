import urllib
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
import re
import settings
from models import Transaction
from models import Client
from models import Donor

class pdt_handler(webapp.RequestHandler):
    def get(self, shortCode):
        client = Client.all().filter('shortCode =', shortCode).get()
        sponsor = client.sponsor
        merchant = sponsor.paypalMerchant

        # Get the transaction id, tx=blahblahblah
        trans_id = self.request.get("tx")


        # Confgure POST args
        args = {}
        # Specify the paypal command
        args["cmd"] ="_notify-synch"
        args["tx"] = trans_id
        args["at"] = merchant.PDTKey

        args = urllib.urlencode(args)

        try:
            # Do a post back to validate
            # the transaction data
            status = urlfetch.fetch(url = settings.PAYPAL_URL,
                                    method = urlfetch.POST,
                                    payload = args).content
        except:
          self.response.out.write("POST Failed")

        lines = status.split('\n')
        if lines[0] == 'SUCCESS':# Check for SUCCESS at the start of the response
            # build a dictionary of key value pair provided by PDT
            lines = lines[1:]
            props = {
                'payment_date' : '',
                'payment_gross': 0,
                'payment_fee': 0,
                'payment_status': '',
                'item_name': '',
                'first_name': '',
                'last_name': '',
                'payer_email': '' }
            for line in lines:
                items = line.split('=')
                if len(items) == 2:
                    key, value = items
                    props[key] = value
                else:
                    props[key] = ''

            # TODO payment_status= complete etc..

            # TODO if client is none

            # Get donor information (create new if not exist)
            donor = Donor.all().filter('email', urllib.unquote(props['payer_email'])).get()
            if donor is None:
                donor = Donor()
                donor.name = "%s %s" % (props['first_name'], props['last_name'])
                donor.email = urllib.unquote( props['payer_email'] )
                donor.put()

            # Create a new transaction (use transaction_id to maintain data uniqueness)
            tx = Transaction.all().filter('txID', trans_id).get()
            if tx is None:
                tx = Transaction( method='PayPal',
                              donor=donor,
                              client=client,
                              txID = trans_id,
                              paymentDate = urllib.unquote(props['payment_date']).replace('+', ' '),
                              amount= float(props['payment_gross']),
                              fee = float(props['payment_fee']) ,
                              paymentStatus = props['payment_status'],
                              note = urllib.unquote(props['item_name']).replace('+', ' '),
                              fulfilled = False
                            )
                tx.put()

            # Regardless of success, user is redirected to thank you screen "/client_short_code#thanks"
            self.response.out.write('<script> window.location = "/'+ shortCode + '#thanks"; </script>')

            # DEBUG code
            # self.response.out.write(urllib.unquote(status))

        else:
            self.response.out.write("Failed<BR>")


class Endpoint(object):

    default_response_text = 'Nothing to see here'
    verify_url = settings.PAYPAL_URL # "https://www.paypal.com/cgi-bin/webscr"

    def do_post(self, url, args):
        return urllib.urlopen(url, urllib.urlencode(args)).read()

    def verify(self, data):
        args = {
            'cmd': '_notify-validate',
        }
        args.update(data)
        return self.do_post(self.verify_url, args) == 'VERIFIED'

    def default_response(self):
        return HttpResponse(self.default_response_text)

    def __call__(self, request):
        r = None
        if request.method == 'POST':
            data = dict(request.POST.items())
            # We need to post that BACK to PayPal to confirm it
            if self.verify(data):
                r = self.process(data)
            else:
                r = self.process_invalid(data)
        if r:
            return r
        else:
            return self.default_response()

    def process(self, data):
        pass

    def process_invalid(self, data):
        pass

class ipn_handler(Endpoint):
    def process(self, data):
        return HttpResponse("IPN received")
        # Do something with valid data from PayPal - e-mail it to yourself,
        # stick it in a database, generate a license key and e-mail it to the
        # user... whatever

    def process_invalid(self, data):
        # Do something with invalid data (could be from anywhere) - you
        # should probably log this somewhere
        pass


class AppEngineEndpoint(Endpoint):

    def do_post(self, url, args):
        from google.appengine.api import urlfetch
        return urlfetch.fetch(
            url = url,
            method = urlfetch.POST,
            payload = urllib.urlencode(args)
        ).content


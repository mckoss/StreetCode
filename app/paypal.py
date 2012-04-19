import urllib
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
import re
import settings
from django.http import HttpResponse
from models import Transaction

class pdt_handler(webapp.RequestHandler):
    def get(self, client):
        # Get the transaction id, tx=blahblahblah
        trans_id = self.request.get("tx")

        # Confgure POST args
        args = {}
        # Specify the paypal command
        args["cmd"] ="_notify-synch"
        args["tx"] = trans_id
        args["at"] = settings.PAYPAL_PDT_KEY

        args = urllib.urlencode(args)

        try:
            # Do a post back to validate
            # the transaction data
            status = urlfetch.fetch(url = settings.PAYPAL_URL,
                                    method = urlfetch.POST,
                                    payload = args).content
        except:
          self.response.out.write("POST Failed")

        # Check for SUCCESS at the start of the response
        lines = status.split(' ')
        if lines[0] == 'SUCCESS':
            lines = line[1:]
            props = {}
            for line in lines:
                (key, value) = line.split('=')
                props[key] = value
            # Check other transaction details here like
            # payment_status etc..

            # TODO Update donation transaction in streetcodes

            client = Client.all().filter('shortCode =', props['item_number']).get()

            donor = Donor.all().filter('email =', props['email']).get()
            if donor is None:
                donor = Donor()
                donor.name = "%s %s" % (props['first'], props['last'])
                donor.email = props['email']
                donor.put()

            tx = Transaction(method='PayPal',
                             donor=donor,
                             client=client,
                             amount=props['amount'])
            tx.put()

            # redirect user to thank you screen "/client_short_code#thanks"
            self.response.out.write('<script> window.location = "/'+ client + '#thanks"; </script>')

            # DEBUG code
            # self.response.out.write("OK<br>")
            # self.response.out.write(urllib.unquote(status))
        else:
            self.response.out.write("Failed")

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


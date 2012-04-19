# Global application settings.
#
# WARNING: Do not put private information in this file (the source
# repository is not secure).
DEBUG = True

SITE_NAME = "StreetCodes"
SITE_ADMIN = "Mike Koss"
ADMIN_EMAIL = "mckoss@startpad.org"

# PayPal keys - INSECURE - these are in a public repo!
PAYPAL_MERCHANT_KEY = "7U9B9CQ4PZXQC"
PAYPAL_PDT_KEY = "TlkFPB-XGaPI9craYTLYMiGA7_-Va_TvdvWA5m0mJurM_dUYm5U2jlpaYg8"
PAYPAL_URL = "https://www.sandbox.paypal.com/cgi-bin/webscr"

# Make all the (string) variables in settings available to templates as {{ var_name }}
# except use lower-case form in templates.
template_vars = {}
for name, value in globals().items():
    if name[0] == '_':
        continue
    if type(value) == str:
        template_vars[name.lower()] = value

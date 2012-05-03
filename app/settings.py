# Global application settings.
#
# WARNING: Do not put private information in this file (the source
# repository is not secure).
DEBUG = False

SITE_NAME = "StreetCodes"
SITE_ADMIN = "Mike Koss"
ADMIN_EMAIL = "mckoss@startpad.org"

if DEBUG is True:
    PAYPAL_URL = "https://www.sandbox.paypal.com/cgi-bin/webscr"
else: 
    PAYPAL_URL = "https://www.paypal.com/cgi-bin/webscr"

# Make all the (string) variables in settings available to templates as {{ var_name }}
# except use lower-case form in templates.
template_vars = {}
for name, value in globals().items():
    if name[0] == '_':
        continue
    if type(value) == str:
        template_vars[name.lower()] = value

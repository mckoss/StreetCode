from google.appengine.ext.webapp import template

import settings
from rest.views import UserHandler


class ClientHandler(UserHandler):
    def get(self, template_type, id):
        self.response.out.write(template.render("templates/client_%s.html" % template_type,
                                                {'id': id,
                                                 'SITE_NAME': settings.SITE_NAME}
                                                ))

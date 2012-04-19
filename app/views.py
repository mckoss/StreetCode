from google.appengine.ext.webapp import template

import settings
from rest.views import UserHandler


class ClientHandler(UserHandler):
    def get(self, template_type, id):
        self.response.out.write(template.render("templates/client_%s.html" % template_type,
                                                {'id': id,
                                                 'site_name': settings.SITE_NAME}
                                                ))

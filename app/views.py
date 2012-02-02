from google.appengine.ext.webapp import template

from user_views import UserHandler


class ClientHandler(UserHandler):
    def get(self, template_type, id):
        self.response.out.write(template.render("templates/client_%s.html" % template_type,
                                                {'id': id,
                                                 'SITE_NAME': settings.SITE_NAME}
                                                ))


class ProfileHandler(UserHandler):
    def get(self, id):
        self.response.out.write(template.render("templates/mobile_profile.html",
                                                {'id': id,
                                                 'SITE_NAME': settings.SITE_NAME}
                                                ))


class DesktopProfileHandler(UserHandler):
    def get(self, id):
        self.response.out.write(template.render("templates/desktop_profile.html",
                                                {'id': id,
                                                 'SITE_NAME': settings.SITE_NAME}
                                                ))

import views
from views import PageHandler
import models


def using(template_name, render_data=None):
    return PageHandler.using(template_name, render_data, package='rest')


def get_paths():
    return [
        # REST views
        ('/data/(\w+)', views.ListHandler),
        ('/data/(\w+)/(\d+)', views.ItemHandler),
        ('/data', views.SchemaHandler),

        # Admin views
        ('/admin', using('admin.html')),
        ('/admin/help', using('help.html')),
        ('/admin/forms', using('main-form.html',
                               {'models': models.rest_models.keys()})),
        ('/admin/forms/(\w+)', using('list-form.html')),
        ('/admin/forms/(\w+)/(\d+)', using('item-form.html')),
        ]

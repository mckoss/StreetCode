import views
from views import get_template_handler
import models


def template_handler(template_name, render_data=None):
    return get_template_handler(template_name, render_data, package='rest')


def get_paths():
    return [
        # REST views
        ('/data/(\w+)', views.ListHandler),
        ('/data/(\w+)/(\d+)', views.ItemHandler),
        ('/data', views.SchemaHandler),

        # Admin views
        ('/admin', template_handler('admin.html')),
        ('/admin/help', template_handler('help.html')),
        ('/admin/forms', template_handler('main-form.html',
                                          {'models': models.rest_models.keys()})),
        ('/admin/forms/(\w+)', template_handler('list-form.html')),
        ('/admin/forms/(\w+)/(\d+)', template_handler('item-form.html')),
        ]

from optparse import make_option
from django.conf import settings
from django.core.management.base import AppCommand

from ratings.models import _RatingsDescriptor


class Command(AppCommand):
    help = "Update the similar items table for any or all apps."

    # Django 1.0.X compatibility.
    verbosity_present = False
    option_list = AppCommand.option_list

    for option in option_list:
        if option.get_opt_string() == '--verbosity':
            verbosity_present = True

    if verbosity_present is False:
        option_list = option_list + (
            make_option('--verbosity', action='store', dest='verbosity',
                default='1', type='choice', choices=['0', '1', '2'],
                help='Verbosity level; 0=minimal output, 1=normal output, 2=all output'
            ),
        )

    def handle(self, *apps, **options):
        self.verbosity = int(options.get('verbosity', 1))

        if not apps:
            from django.db.models import get_app
            apps = []

            for app in settings.INSTALLED_APPS:
                try:
                    app_label = app.split('.')[-1]
                    get_app(app_label)
                    apps.append(app_label)
                except:
                    pass

        return super(Command, self).handle(*apps, **options)

    def handle_app(self, app, **options):
        from django.db.models import get_models

        for model in get_models(app):
            for k, v in model.__dict__.iteritems():
                if isinstance(v, _RatingsDescriptor):
                    if self.verbosity > 0:
                        print 'Updating the %s field of %s' % (k, model)
                    getattr(model, k).update_similar_items()

Installation
============

You can pip install django-simple-ratings::

    pip install django-simple-ratings

Alternatively, you can use the version hosted on GitHub, which may contain new
or undocumented features::

    git clone git://github.com/coleifer/django-simple-ratings.git
    cd django-simple-ratings
    python setup.py install


Installing the dependencies
---------------------------

The project currently depends on `django-generic-aggregation <https://github.com/coleifer/django-generic-aggregation>`_.
You can manually install using pip or install from the "pip_requirements.txt" file
bundled with the source::

    pip install -r pip_requirements.txt


Adding to your Django Project
--------------------------------

After installing, adding relationships to your projects is a snap.  First,
add it to your projects' ``INSTALLED_APPS``::
    
    # settings.py
    INSTALLED_APPS = [
        ...
        'ratings'
    ]

Next you'll need to run a ``syncdb``::

    django-admin.py syncdb

If you're using `south` for schema migrations, you can use the migrations
provided by the app.

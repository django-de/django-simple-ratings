Getting Started
===============

The goal of this project was to make it really simple to add ratings to models.

.. code-block:: python

    from django.db import models
    from rating.models import Ratings
    
    class Food(models.Model):
        name = models.CharField(max_length=50)
        
        ratings = Ratings()
        
Now, you can add ratings to various models:

.. code-block:: python

    >>> apple.ratings.rate(user=john, score=1)
    <RatedItem: apple rated 1 by john>

    >>> apple.ratings.rate(user=jane, score=5)
    <RatedItem: apple rated 5 by jane>

You can query a model instance and retrieve all the individual :class:`RatedItem`
instances connected to it:

.. code-block:: python
    
    >>> apple.ratings.all()
    [<RatedItem: apple rated 1 by john>, <RatedItem: apple rated 5 by jane>]

Most interestingly, you can perform aggregation across :class:`RatedItem` instances
to obtain values like "cumulative score" and "average score".

.. code-block:: python

    >>> apple.ratings.cumulative_score()
    6

    >>> apple.ratings.average_score()
    3.0

Lastly, you can order model instances by their rating.  By default the "score"
will be a sum of all ratings, but the actual aggregator function used can be
specified manually.

.. code-block:: python

    >>> Food.ratings.order_by_rating()
    [<Food: apple>, <Food: orange>]
    
    >>> Food.ratings.order_by_rating(aggregator=models.Avg)
    [<Food: apple>, <Food: orange>]

If you want to see what a User's favorite objects were, you could filter
the ratings by that user, then order by rating:

.. code-block:: python

    >>> johns_items = Food.ratings.filter(user=john).order_by_rating()
    >>> johns_items
    [<Food: orange>, <Food: apple>]
    >>> johns_items[0].score # what did john rate orange?
    3.0
    >>> johns_items[1].score # what did john rate apple?
    1.0


Use GFKs, FKs, whatever
-----------------------

By default, whenever you add ``Ratings()`` to your model it uses the :class:`RatedItem` model
which uses a ``Generic ForeignKey`` on it.  Suppose you are only rating one thing, or would like to
have an explicit database constraint -- that's no problem.  You can provide a
custom :class:`RatedItem` model with a ``ForeignKey`` instead of a ``GFK``.  Here's the example
from the tests:

.. code-block:: python

    class BeverageRating(RatedItemBase):
        content_object = models.ForeignKey('Beverage')


    class Beverage(models.Model):
        name = models.CharField(max_length=50)
        
        ratings = Ratings(BeverageRating)
        
        def __unicode__(self):
            return self.name


The API is exactly the same.


URLs, Views, and Templates
--------------------------

The app comes configured with views for adding and removing ratings on content
items.  These urls assume you have configured your ``ROOT_URLCONF`` like this::

    urlpatterns = patterns('',
        # ... urls ...
        url(r'^ratings/', include('ratings.urls')),
    )

URLs to add and remove ratings look like this:

* ``/ratings/rate/<content-type-id>/<object-id>/<score>/`` to add or update a rating
* ``/ratings/unrate/<content-type-id>/<object-id>/`` to unrate an object

The urls support floating point scores and non-integer primary keys.

.. warning:: these views only accept POST requests.

Using the template filter to generate urls
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

I'd recommend using the template filter to generate urls as it does the annoying
lookups for you::

    {% if not request.user|has_rated:object %}
      <p>
        <a href="{{ object|rate_url:1 }}">+1</a> or 
        <a href="{{ object|rate_url:-1 }}">-1</a>
      </p>
    {% else %}
      <p>You have rated this item {{ object|rating_score:request.user }}</p>
      <p><a href="{{ object|unrate_url }}">Remove rating</a></p>
    {% endif %}

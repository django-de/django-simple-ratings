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

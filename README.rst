=====================
django-simple-ratings
=====================

a simple, extensible rating system.

dependencies:

* django-generic-aggregation: http://github.com/coleifer/django-generic-aggregation


With a little bit more
----------------------

also, a playground for different stuff i've been reading about in 
*programming collective intelligence*, by toby segaran.

this stuff lives in utils.py and is there if you want to experiment (or
contribute!).


Getting started
---------------

you'd like to add ratings to some model::

    from django.db import models
    from rating.models import Ratings
    
    class Food(models.Model):
        name = models.CharField(max_length=50)
        
        ratings = Ratings()
        
now, you can::

    # add ratings to things
    >>> apple.ratings.rate(user=john, score=1)
    <RatedItem: apple rated 1 by john>

    >>> apple.ratings.rate(user=jane, score=5)
    <RatedItem: apple rated 5 by jane>
    
    # get interesting aggregate data
    >>> apple.ratings.all()
    [<RatedItem: apple rated 1 by john>, <RatedItem: apple rated 5 by jane>]

    >>> apple.ratings.cumulative_score()
    6

    >>> apple.ratings.average_score()
    3.0
    
    # order things by their rating
    >>> Food.ratings.order_by_rating()
    [<Food: apple>, <Food: orange>]


Use GFKs, FKs, whatever
-----------------------

By default, whenever you add Ratings() to your model it uses the RatedItem model
which has a GFK on it.  Suppose you are only rating one thing, or would like to
have an explicit database constraint -- that's no problem.  You can provide a
custom RatedItem model with a ForeignKey instead of a GFK.  Here's the example
from the tests::

    class BeverageRating(RatedItemBase):
        content_object = models.ForeignKey('Beverage')


    class Beverage(models.Model):
        name = models.CharField(max_length=50)
        
        ratings = Ratings(BeverageRating)
        
        def __unicode__(self):
            return self.name


The API is exactly the same.

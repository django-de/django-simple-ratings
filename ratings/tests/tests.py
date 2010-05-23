from django.contrib.auth.models import User
from django.test import TestCase

from ratings.models import RatedItem
from ratings.tests.models import Food, Beverage, BeverageRating


class BaseRatingsTestCase(TestCase):
    def setUp(self):
        self.apple = Food.objects.create(name='apple')
        self.orange = Food.objects.create(name='orange')
        
        self.coke = Beverage.objects.create(name='coke')
        self.pepsi = Beverage.objects.create(name='pepsi')
        
        self.john = User.objects.create_user('john', 'john@doe.com')
        self.jane = User.objects.create_user('jane', 'jane@doe.com')

    def _sort_by_pk(self, list_or_qs):
        # decorate, sort, undecorate using the pk of the items
        # in the list or queryset
        annotated = [(item.pk, item) for item in list_or_qs]
        annotated.sort()
        return map(lambda item_tuple: item_tuple[1], annotated)
    
    def assertQuerysetEqual(self, a, b):
        # assert list or queryset a is the same as list or queryset b
        return self.assertEqual(self._sort_by_pk(a), self._sort_by_pk(b))


class RatingsTestCase(BaseRatingsTestCase):
    def test_add(self):
        rating = RatedItem(user=self.john, score=1)
        self.apple.ratings.add(rating)
        
        # make sure the apple rating got added
        self.assertEqual(self.apple.ratings.count(), 1)
        
        # get the rating and check that it saved correctly
        apple_rating = self.apple.ratings.all()[0]
        self.assertEqual(unicode(apple_rating), 'apple rated 1 by john')
        
        # get the rating another way and check that it works
        apple_rating_alt = self.john.rateditems.all()[0]
        self.assertEqual(apple_rating, apple_rating_alt)

        rating2 = RatedItem(user=self.john, score=-1)
        self.orange.ratings.add(rating2)
        
        # check that the orange rating got added and that our apple rating is ok
        self.assertEqual(self.orange.ratings.count(), 1)
        self.assertEqual(self.apple.ratings.count(), 1)

        self.assertEqual(self.john.rateditems.count(), 2)
    
    def test_remove(self):
        rating = RatedItem(user=self.john, score=1)
        self.apple.ratings.add(rating)
        
        rating2 = RatedItem(user=self.jane, score=-1)
        self.apple.ratings.add(rating2)
        
        rating3 = RatedItem(user=self.john, score=-1)
        self.orange.ratings.add(rating3)
        
        # check to see that john's apple rating gets removed
        self.apple.ratings.remove(rating)
        self.assertEqual(self.apple.ratings.count(), 1)
        self.assertEqual(self.apple.ratings.all()[0], rating2)
        
        # make sure the orange's rating is still intact
        self.assertEqual(self.orange.ratings.count(), 1)
        
        # trying to remove the orange rating from the apple doesn't work
        self.assertRaises(RatedItem.DoesNotExist, self.apple.ratings.remove, rating3)
        self.assertEqual(self.orange.ratings.count(), 1)
    
    def test_clear(self):
        rating = RatedItem(user=self.john, score=1)
        self.apple.ratings.add(rating)
        
        rating2 = RatedItem(user=self.jane, score=-1)
        self.apple.ratings.add(rating2)
        
        rating3 = RatedItem(user=self.john, score=-1)
        self.orange.ratings.add(rating3)
        
        # check to see that we can clear apple's ratings
        self.apple.ratings.clear()
        self.assertEqual(self.apple.ratings.count(), 0)
        self.assertEqual(self.orange.ratings.count(), 1)
    
    def test_rate_method(self):
        rating1 = self.apple.ratings.rate(self.john, 1)
        rating2 = self.apple.ratings.rate(self.jane, -1)
        rating3 = self.orange.ratings.rate(self.john, -1)
        
        self.assertQuerysetEqual(self.apple.ratings.all(), [rating1, rating2])
        self.assertQuerysetEqual(self.orange.ratings.all(), [rating3])
        
        self.assertEqual(rating1.content_object, self.apple)
        self.assertEqual(rating2.content_object, self.apple)
        self.assertEqual(rating3.content_object, self.orange)
        
        rating1_alt = self.apple.ratings.rate(self.john, 1000000)
        
        # get_or_create'd the rating based on user, so count stays the same
        self.assertEqual(self.apple.ratings.count(), 2)
        self.assertEqual(rating1.pk, rating1_alt.pk)
        self.assertEqual(rating1_alt.score, 1000000)
    
    def test_scoring(self):
        rating1 = self.apple.ratings.rate(self.john, 1)
        rating2 = self.apple.ratings.rate(self.jane, -1)
        rating3 = self.orange.ratings.rate(self.john, -1)
        
        self.assertEqual(self.apple.ratings.cumulative_score(), 0)
        self.assertEqual(self.apple.ratings.average_score(), 0)
        
        self.apple.ratings.rate(self.john, 10)
        self.assertEqual(self.apple.ratings.cumulative_score(), 9)
        self.assertEqual(self.apple.ratings.average_score(), 4.5)
    
    def test_all(self):
        rating = RatedItem(user=self.john, score=1)
        self.apple.ratings.add(rating)
        
        rating2 = RatedItem(user=self.jane, score=-1)
        self.apple.ratings.add(rating2)
        
        rating3 = RatedItem(user=self.john, score=-1)
        self.orange.ratings.add(rating3)
        
        self.assertQuerysetEqual(self.apple.ratings.all(), [rating, rating2])
        self.assertQuerysetEqual(self.orange.ratings.all(), [rating3])
        self.assertQuerysetEqual(Food.ratings.all(), [rating, rating2, rating3])
    
    def test_ordering(self):
        rating1 = self.apple.ratings.rate(self.john, 1)
        rating2 = self.apple.ratings.rate(self.jane, -1)
        rating3 = self.orange.ratings.rate(self.john, 1)
        
        foods = Food.ratings.order_by_rating()
        self.assertQuerysetEqual(foods, [self.orange, self.apple])
        
        self.assertEqual(foods[0].score, 1)
        self.assertEqual(foods[1].score, 0)
        
        self.apple.ratings.rate(self.john, 3)
        foods = Food.ratings.order_by_rating()
        self.assertQuerysetEqual(foods, [self.apple, self.orange])
    
        self.assertEqual(foods[0].score, 2)
        self.assertEqual(foods[1].score, 1)

class CustomModelRatingsTestCase(BaseRatingsTestCase):
    def test_add(self):
        rating = BeverageRating(user=self.john, score=1)
        self.coke.ratings.add(rating)
        
        # make sure the coke rating got added
        self.assertEqual(self.coke.ratings.count(), 1)
        
        # get the rating and check that it saved correctly
        coke_rating = self.coke.ratings.all()[0]
        self.assertEqual(unicode(coke_rating), 'coke rated 1 by john')
        
        # get the rating another way and check that it works
        coke_rating_alt = self.john.beverageratings.all()[0]
        self.assertEqual(coke_rating, coke_rating_alt)

        rating2 = BeverageRating(user=self.john, score=-1)
        self.pepsi.ratings.add(rating2)
        
        # check that the pepsi rating got added and that our coke rating is ok
        self.assertEqual(self.pepsi.ratings.count(), 1)
        self.assertEqual(self.coke.ratings.count(), 1)

        self.assertEqual(self.john.beverageratings.count(), 2)
    
    def test_remove(self):
        rating = BeverageRating(user=self.john, score=1)
        self.coke.ratings.add(rating)
        
        rating2 = BeverageRating(user=self.jane, score=-1)
        self.coke.ratings.add(rating2)
        
        rating3 = BeverageRating(user=self.john, score=-1)
        self.pepsi.ratings.add(rating3)
        
        # check to see that john's coke rating gets removed
        self.coke.ratings.remove(rating)
        self.assertEqual(self.coke.ratings.count(), 1)
        self.assertEqual(self.coke.ratings.all()[0], rating2)
        
        # make sure the pepsi's rating is still intact
        self.assertEqual(self.pepsi.ratings.count(), 1)
        
        # trying to remove the pepsi rating from the coke doesn't work
        self.assertRaises(BeverageRating.DoesNotExist, self.coke.ratings.remove, rating3)
        self.assertEqual(self.pepsi.ratings.count(), 1)
    
    def test_clear(self):
        rating = BeverageRating(user=self.john, score=1)
        self.coke.ratings.add(rating)
        
        rating2 = BeverageRating(user=self.jane, score=-1)
        self.coke.ratings.add(rating2)
        
        rating3 = BeverageRating(user=self.john, score=-1)
        self.pepsi.ratings.add(rating3)
        
        # check to see that we can clear coke's ratings
        self.coke.ratings.clear()
        self.assertEqual(self.coke.ratings.count(), 0)
        self.assertEqual(self.pepsi.ratings.count(), 1)
    
    def test_rate_method(self):
        rating1 = self.coke.ratings.rate(self.john, 1)
        rating2 = self.coke.ratings.rate(self.jane, -1)
        rating3 = self.pepsi.ratings.rate(self.john, -1)
        
        self.assertQuerysetEqual(self.coke.ratings.all(), [rating1, rating2])
        self.assertQuerysetEqual(self.pepsi.ratings.all(), [rating3])
        
        self.assertEqual(rating1.content_object, self.coke)
        self.assertEqual(rating2.content_object, self.coke)
        self.assertEqual(rating3.content_object, self.pepsi)
        
        rating1_alt = self.coke.ratings.rate(self.john, 1000000)
        
        # get_or_create'd the rating based on user, so count stays the same
        self.assertEqual(self.coke.ratings.count(), 2)
        self.assertEqual(rating1.pk, rating1_alt.pk)
        self.assertEqual(rating1_alt.score, 1000000)
    
    def test_all(self):
        rating = BeverageRating(user=self.john, score=1)
        self.coke.ratings.add(rating)
        
        rating2 = BeverageRating(user=self.jane, score=-1)
        self.coke.ratings.add(rating2)
        
        rating3 = BeverageRating(user=self.john, score=-1)
        self.pepsi.ratings.add(rating3)
        
        self.assertQuerysetEqual(self.coke.ratings.all(), [rating, rating2])
        self.assertQuerysetEqual(self.pepsi.ratings.all(), [rating3])
        self.assertQuerysetEqual(Beverage.ratings.all(), [rating, rating2, rating3])
   
    def test_ordering(self):
        rating1 = self.coke.ratings.rate(self.john, 1)
        rating2 = self.coke.ratings.rate(self.jane, -1)
        rating3 = self.pepsi.ratings.rate(self.john, 1)
        
        beverages = Beverage.ratings.order_by_rating()
        self.assertQuerysetEqual(beverages, [self.pepsi, self.coke])
        
        self.assertEqual(beverages[0].score, 1)
        self.assertEqual(beverages[1].score, 0)
        
        self.coke.ratings.rate(self.john, 3)
        beverages = Beverage.ratings.order_by_rating()
        self.assertQuerysetEqual(beverages, [self.coke, self.pepsi])
        
        self.assertEqual(beverages[0].score, 2)
        self.assertEqual(beverages[1].score, 1)

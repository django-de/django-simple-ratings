import django
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import models, IntegrityError
from django.template.defaultfilters import slugify


class RatedItemBase(models.Model):
    score = models.IntegerField(default=0)
    user = models.ForeignKey(User, related_name='%(class)ss')

    def __unicode__(self):
        return "%s rated %s by %s" % (self.content_object, self.score, self.user)
    
    class Meta:
        abstract = True

    @classmethod
    def lookup_kwargs(cls, instance):
        return {'content_object': instance}
    
    @classmethod
    def base_kwargs(cls, model_class):
        return {}


class RatedItem(RatedItemBase):
    object_id = models.IntegerField()
    content_type = models.ForeignKey(ContentType, related_name="rated_items")
    content_object = GenericForeignKey()

    @classmethod
    def lookup_kwargs(cls, instance):
        return {
            'object_id': instance.pk,
            'content_type': ContentType.objects.get_for_model(instance)
        }
    
    @classmethod
    def base_kwargs(cls, model_class):
        return {'content_type': ContentType.objects.get_for_model(model_class)}


# this goes on your model
class Ratings(object):
    def __init__(self, rating_model=None):
        self.rating_model = rating_model or RatedItem
        
    def contribute_to_class(self, cls, name):
        # set up the ForeignRelatedObjectsDescriptor right hyah
        setattr(cls, name, _RatingsDescriptor(cls, self.rating_model, name))


class _RatingsDescriptor(object):
    def __init__(self, rated_model, rating_model, rating_field):
        self.rated_model = rated_model
        self.rating_model = rating_model
        self.rating_field = rating_field
    
    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        return self.create_manager(instance,
                self.rating_model._default_manager.__class__)

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError, "Manager must be accessed via instance"

        manager = self.__get__(instance)
        manager.add(*value)

    def delete_manager(self, instance):
        """
        Returns a queryset based on the related model's base manager (rather
        than the default manager, as returned by __get__). Used by
        Model.delete().
        """
        return self.create_manager(instance,
                self.rating_model._base_manager.__class__)

    def create_manager(self, instance, superclass):
        """
        Dynamically create a RelatedManager to handle the back side of the (G)FK
        """
        rel_field = self.rating_field
        rel_model = self.rating_model

        class RelatedManager(superclass):
            def get_query_set(self):
                return superclass.get_query_set(self).filter(**(self.core_filters))

            def add(self, *objs):
                lookup_kwargs = rel_model.lookup_kwargs(instance)
                for obj in objs:
                    if not isinstance(obj, self.model):
                        raise TypeError, "'%s' instance expected" % self.model._meta.object_name
                    for (k, v) in lookup_kwargs.iteritems():
                        setattr(obj, k, v)
                    obj.save()
            add.alters_data = True

            def create(self, **kwargs):
                kwargs.update(rel_model.lookup_kwargs(instance))
                return super(RelatedManager, self).create(**kwargs)
            create.alters_data = True

            def get_or_create(self, **kwargs):
                kwargs.update(rel_model.lookup_kwargs(instance))
                return super(RelatedManager, self).get_or_create(**kwargs)
            get_or_create.alters_data = True

            def remove(self, *objs):
                for obj in objs:
                    # Is obj actually part of this descriptor set?
                    if obj in self.all():
                        obj.delete()
                    else:
                        raise rel_model.DoesNotExist, "%r is not related to %r." % (obj, instance)
            remove.alters_data = True

            def clear(self):
                self.all().delete()
            clear.alters_data = True
            
            def rate(self, user, score):
                rating, created = self.get_or_create(user=user)
                if created or score != rating.score:
                    rating.score = score
                    rating.save()
                return rating
            
            def perform_aggregation(self, aggregator):
                score = self.all().aggregate(agg=aggregator('score'))
                return score['agg']
            
            def cumulative_score(self):
                # simply the sum of all scores, useful for +1/-1
                return self.perform_aggregation(models.Sum)
            
            def average_score(self):
                # the average of all the scores, useful for 1-5
                return self.perform_aggregation(models.Avg)
            
            def standard_deviation(self):
                # the standard deviation of all the scores, useful for 1-5
                return self.perform_aggregation(models.StdDev)
            
            def variance(self):
                # the variance of all the scores, useful for 1-5
                return self.perform_aggregation(models.Variance)

        manager = RelatedManager()
        manager.core_filters = rel_model.lookup_kwargs(instance)
        manager.model = rel_model

        return manager
    
    def all(self):
        query = self.rating_model.base_kwargs(self.rated_model)
        return self.rating_model._default_manager.filter(**query)
    
    def get_content_object_field(self):
        opts = self.rating_model._meta
        for virtual_field in opts.virtual_fields:
            if virtual_field.name == 'content_object':
                return virtual_field
        return opts.get_field('content_object')
    
    @property
    def is_gfk(self):
        return isinstance(self.get_content_object_field(), GenericForeignKey)
    
    def order_by_rating(self, aggregator=models.Sum, descending=True):
        ordering = descending and '-score' or 'score'
        if not self.is_gfk:
            related_field = self.get_content_object_field()
            qn = related_field.related_query_name()
            qs = self.rated_model._default_manager.all()
            return qs.annotate(score=models.Sum('%s__score' % qn)).order_by(ordering)
        # nasty.
        base_qs = self.all()
        results = base_qs.values_list('object_id').annotate(score=aggregator('score')).order_by(ordering)
        ordered_pks = map(lambda t: t[0], results)
        objects = self.rated_model._default_manager.in_bulk(ordered_pks)
        return [objects[pk] for pk in ordered_pks]

from math import sqrt

from django.contrib.auth.models import User
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import connection

def get_content_object_field(rating_model):
    opts = rating_model._meta
    for virtual_field in opts.virtual_fields:
        if virtual_field.name == 'content_object':
            return virtual_field # break out early
    return opts.get_field('content_object')

def is_gfk(content_field):
    return isinstance(content_field, GenericForeignKey)

def sim_euclidean_distance(ratings_queryset, factor_a, factor_b):
    rating_model = ratings_queryset.model
    
    if isinstance(factor_a, User):
        filter_field = 'user_id'
        match_on = 'hashed'
        lookup_a = factor_a.pk
        lookup_b = factor_b.pk
    else:
        filter_field = 'hashed'
        match_on = 'user_id'
        lookup_a = rating_model(content_object=factor_a).generate_hash()
        lookup_b = rating_model(content_object=factor_b).generate_hash()

    sql = """
    SELECT r1.score - r2.score AS diff
    FROM
        %(ratings_table)s AS r1,
        %(ratings_table)s AS r2
    WHERE
        r1.%(filter_field)s = "%(lookup_a)s" AND
        r2.%(filter_field)s = "%(lookup_b)s" AND
        r1.%(match_on)s = r2.%(match_on)s
        %(queryset_filter)s
    """
    
    rating_query = ratings_queryset.values_list('pk').query
    if rating_query.where.as_sql()[0] is None:
        queryset_filter = ''
    else:
        rating_qs_sql = rating_query.as_sql()[0] % rating_query.as_sql()[1]
        queryset_filter = ' AND r1.id IN (%s)' % rating_qs_sql
    
    params = {
        'ratings_table': rating_model._meta.db_table,
        'filter_field': filter_field,
        'match_on': match_on,
        'lookup_a': lookup_a,
        'lookup_b': lookup_b,
        'queryset_filter': queryset_filter
    }

    cursor = connection.cursor()
    cursor.execute(sql % params)
    
    sum_of_squares = 0
    while True:
        result = cursor.fetchone()
        if result is None:
            break
        sum_of_squares += result[0] ** 2
    
    return 1 / (1 + sum_of_squares)

def sim_pearson_correlation(ratings_queryset, factor_a, factor_b):
    rating_model = ratings_queryset.model
    
    if isinstance(factor_a, User):
        filter_field = 'user_id'
        match_on = 'hashed'
        lookup_a = factor_a.pk
        lookup_b = factor_b.pk
    else:
        filter_field = 'hashed'
        match_on = 'user_id'
        lookup_a = rating_model(content_object=factor_a).generate_hash()
        lookup_b = rating_model(content_object=factor_b).generate_hash()

    sql = """
    SELECT 
        SUM(r1.score) AS r1_sum, 
        SUM(r2.score) AS r2_sum, 
        SUM(r1.score*r1.score) AS r1_square_sum, 
        SUM(r2.score*r2.score) AS r2_square_sum,
        SUM(r1.score*r2.score) AS p_sum,
        COUNT(r1.id) AS sample_size
    FROM
        %(ratings_table)s AS r1,
        %(ratings_table)s AS r2
    WHERE
        r1.%(filter_field)s = "%(lookup_a)s" AND
        r2.%(filter_field)s = "%(lookup_b)s" AND
        r1.%(match_on)s = r2.%(match_on)s
        %(queryset_filter)s
    """
    
    rating_query = ratings_queryset.values_list('pk').query
    if rating_query.where.as_sql()[0] is None:
        queryset_filter = ''
    else:
        rating_qs_sql = rating_query.as_sql()[0] % rating_query.as_sql()[1]
        queryset_filter = ' AND r1.id IN (%s)' % rating_qs_sql
    
    params = {
        'ratings_table': rating_model._meta.db_table,
        'filter_field': filter_field,
        'match_on': match_on,
        'lookup_a': lookup_a,
        'lookup_b': lookup_b,
        'queryset_filter': queryset_filter
    }

    cursor = connection.cursor()
    cursor.execute(sql % params)

    result = cursor.fetchone()

    if not result:
        return 0

    sum1, sum2, sum1_sq, sum2_sq, psum, sample_size = result
    
    num = psum - (sum1 * sum2 / sample_size)
    den = sqrt((sum1_sq - pow(sum1, 2) / sample_size) * (sum2_sq - pow(sum2, 2) / sample_size))
    
    if den == 0:
        return 0
    
    return num / den

def top_matches(ratings_queryset, people, person, n=5, 
                similarity=sim_pearson_correlation):
    scores = [
        (similarity(ratings_queryset, person, other), other)
            for other in people if other != person]
    scores.sort()
    scores.reverse()
    return scores[:n]

def recommendations(ratings_queryset, people, person,
                    similarity=sim_pearson_correlation):
    rating_model = ratings_queryset.model
    
    already_rated = ratings_queryset.filter(user=person).values_list('hashed')
    
    totals = {}
    sim_sums = {}
    
    for other in people:
        if other == person:
            continue
        
        sim = similarity(ratings_queryset, person, other)
        
        if sim <= 0:
            continue
        
        # now, score the items person hasn't rated yet
        for item in ratings_queryset.filter(user=other).exclude(hashed__in=already_rated):
            totals.setdefault(item.content_object, 0)
            totals[item.content_object] += (item.score * sim)
            
            sim_sums.setdefault(item.content_object, 0)
            sim_sums[item.content_object] += sim
    
    rankings = [(total / sim_sums[pk], pk) for pk, total in totals.iteritems()]
    
    rankings.sort()
    rankings.reverse()
    return rankings

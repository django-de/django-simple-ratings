from django.contrib.contenttypes.generic import GenericForeignKey

def get_content_object_field(rating_model):
    opts = rating_model._meta
    for virtual_field in opts.virtual_fields:
        if virtual_field.name == 'content_object':
            return virtual_field # break out early
    return opts.get_field('content_object')

def is_gfk(rating_model):
    return isinstance(get_content_object_field(rating_model), GenericForeignKey)

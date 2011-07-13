from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import get_object_or_404


@login_required
def rate_object(request, ct, pk, score=1, add=True):
    if not request.method == 'POST':
        return HttpResponseNotAllowed('Invalid request method: "%s". Must be POST.' % request.method)
    
    ctype = get_object_or_404(ContentType, pk=ct)
    model_class = ctype.model_class()
    
    if not hasattr(model_class, '_ratings_field'):
        raise Http404('Model class %s does not support ratings' % model_class)
    
    obj = get_object_or_404(model_class, pk=pk)
    
    ratings_descriptor = getattr(obj, obj._ratings_field)
    
    if add:
        score = '.' in score and float(score) or int(score)
        ratings_descriptor.rate(request.user, score)
    else:
        ratings_descriptor.unrate(request.user)
    
    if request.is_ajax():
        return HttpResponse('{"success": true}', mimetype='application/json')
    
    return HttpResponseRedirect(request.REQUEST.get('next') or request.META['HTTP_REFERER'])

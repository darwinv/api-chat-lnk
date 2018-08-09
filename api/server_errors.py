import sys
from django.http import HttpResponse
from django.core.handlers import base
from django.urls import get_resolver, set_urlconf
from django.views.debug import ExceptionReporter
from api.logger import manager
logger = manager.setup_log(__name__)

def handler500(request):
    if hasattr(request, 'urlconf'):
        urlconf = request.urlconf
        set_urlconf(urlconf)
        resolver = get_resolver(urlconf)
    else:
        resolver = get_resolver()

    resolver_match = resolver.resolve(request.path_info)
    callback, callback_args, callback_kwargs = resolver_match
    request.resolver_match = resolver_match

    obj = base.BaseHandler
    wrapped_callback = obj.make_view_atomic(obj, callback)

    try:
        response = wrapped_callback(request, *callback_args, **callback_kwargs)
    except Exception as e:

        exc_type, exc_value, tb = sys.exc_info()
        reporter = ExceptionReporter(request, exc_type, exc_value, tb)
        frames = reporter.get_traceback_frames()
        
        traceback_string = ""
        for frame in frames:
            traceback_string += "({},{})".format(str(frame['lineno']), str(frame['filename']))

        logger.critical("|URL->| {} |ERROR->| {} |TRACEBACK->| {}".format(request,\
                                                                            e, traceback_string))

        return HttpResponse(status=500)

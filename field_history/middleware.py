from .tracker import FieldHistoryTracker
from django import VERSION


if VERSION >= (1, 10):
    from django.utils.deprecation import MiddlewareMixin

    class FieldHistoryMiddleware(MiddlewareMixin):

        def process_request(self, request):
            FieldHistoryTracker.thread.request = request
else:
    class FieldHistoryMiddleware(object):

        def process_request(self, request):
            FieldHistoryTracker.thread.request = request

from django.utils.deprecation import MiddlewareMixin

from .tracker import FieldHistoryTracker


class FieldHistoryMiddleware(MiddlewareMixin):

    def process_request(self, request):
        FieldHistoryTracker.thread.request = request

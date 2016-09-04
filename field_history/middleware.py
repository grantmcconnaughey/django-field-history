from .tracker import FieldHistoryTracker
from django.utils.deprecation import MiddlewareMixin


class FieldHistoryMiddleware(MiddlewareMixin):

    def process_request(self, request):
        FieldHistoryTracker.thread.request = request

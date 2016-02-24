from .tracker import FieldHistoryTracker


class FieldHistoryMiddleware(object):

    def process_request(self, request):
        FieldHistoryTracker.thread.request = request

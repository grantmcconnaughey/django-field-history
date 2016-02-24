from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse

from .models import PizzaOrder


@login_required
def test_view(request):
    PizzaOrder.objects.create(status='ORDERED')
    return HttpResponse()

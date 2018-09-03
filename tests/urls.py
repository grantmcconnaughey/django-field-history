from django.conf.urls import url
from django.contrib import admin

from . import views


urlpatterns = [
    url(r"^$", views.test_view, name="index"),
    url(r"^admin/", admin.site.urls),
]

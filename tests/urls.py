from django.conf.urls import include, url
from django.contrib import admin

from . import views


urlpatterns = [
    url(r"^$", views.test_view, name="index"),
    url(r"^admin/", include(admin.site.urls)),
]

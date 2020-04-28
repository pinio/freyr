from django.urls import path

from .views import percentiles

urlpatterns = [
    path("percentiles/", percentiles),
]

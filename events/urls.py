
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('events', views.get_events, name='get_events')
]
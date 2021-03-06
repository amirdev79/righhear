
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get_events/', views.get_events, name='get_events'),
    path('get_user_selected_events/', views.get_user_selected_events, name="get_user_selected_events"),
    path('get_categories/', views.get_categories, name='get_categories'),
]

from django.urls import path

from . import views

urlpatterns = [
    path('sign_in/', views.sign_in, name='sign_in'),
    path('add_swipe_action/', views.add_swipe_action, name='add_swipe_action'),
    path('update_user_profile/', views.update_user_profile, name='update_user_profile'),
]

from django.urls import path

from . import views

urlpatterns = [
    path('sign_in/', views.sign_in, name='sign_in'),
    path('sign_in_with_facebook/', views.sign_in_with_facebook, name='sign_in_with_facebook'),
    path('add_swipe_action/', views.add_swipe_action, name='add_swipe_action'),
    path('update_user_profile/', views.update_user_profile, name='update_user_profile'),
    path('landing_page/', views.landing_page, name='landing_page'),
    path('add_user_message/', views.add_user_message, name='add_user_message'),
]
from django.urls import path
from . import views
app_name = 'djangoapp'
urlpatterns = [
    path('login', views.login_user, name='login'),
    path('logout', views.logout_request, name='logout'),
    path('register', views.registration, name='register'),
    path('user', views.current_user, name='current_user'),
    path('get_dealers', views.get_dealerships),
    path('get_dealers/<str:state>', views.get_dealerships),
    path('dealer/<int:dealer_id>', views.get_dealer_details),
    path('reviews/dealer/<int:dealer_id>', views.get_dealer_reviews),
    path('get_cars', views.get_cars),
    path('add_review', views.add_review),
]

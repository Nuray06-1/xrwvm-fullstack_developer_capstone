from django.urls import path
from . import views
app_name='djangoapp'
urlpatterns=[
    path('session',views.session),path('login',views.login_user),
    path('logout',views.logout_user),path('register',views.registration),
    path('get_dealers',views.dealers),path('dealer/<int:dealer_id>',views.dealer),
    path('get_reviews/<int:dealer_id>',views.reviews),path('get_cars',views.cars),
    path('add_review',views.add_review),
]

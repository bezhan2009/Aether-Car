from django.urls import path
from . import views

urlpatterns = [
    path('', views.CarList.as_view(), name='Cars'),
    path('<int:_id>/', views.CarDetail.as_view(), name='car_detail'),
    path('<int:user_id>/user/', views.CarUser.as_view(), name='car_user'),
]

from django.urls import path
from . import views
urlpatterns = [
    path('', views.CategoryList.as_view(), name='model-list'),
    path('<int:pk>/', views.CategoryDetails.as_view(), name='model-detail'),
]

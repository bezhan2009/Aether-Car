from django.urls import path
from .views import FeaturedCarList, FeaturedProductDetail

urlpatterns = [
    path('', FeaturedCarList.as_view(), name='featuredProductsList'),
    path('detail/<int:pk>', FeaturedProductDetail.as_view(), name='featuredProductsDetail'),
]

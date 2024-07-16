from rest_framework import serializers

from featured_productapp.models import FeaturedCar


class FeaturesCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeaturedCar
        fields = '__all__'

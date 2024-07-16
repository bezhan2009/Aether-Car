from rest_framework import serializers
from modelapp.models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = '__all__'

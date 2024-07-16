from rest_framework import serializers
from carapp.models import *
from modelapp.serializers import CategorySerializer


class CarImageSerializer(serializers.ModelSerializer):
    product = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to="product_images/")

    class Meta:
        model = CarImage
        fields = ['image']


class CarSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), required=False)
    images = CarImageSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = ['id', 'user', 'model', 'title', 'description', 'price', 'amount', 'images', 'default_account',
                  "views"]


class CarUpDateNewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserProfile.objects.all(), required=False)
    images = CarImageSerializer(many=True, read_only=True)
    model = serializers.PrimaryKeyRelatedField(queryset=Model.objects.all(), required=False)

    class Meta:
        model = Car
        fields = ['id', 'user', 'model', 'title', 'description', 'price', 'amount', 'images', 'default_account',
                  "views"]


class CarUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    price = serializers.FloatField(required=False)
    amount = serializers.IntegerField(required=False)
    is_deleted = serializers.BooleanField(required=False)

    def validate(self, data):
        # Your validation logic if needed
        return data


class CarQuerySerializer(serializers.Serializer):
    show_own_products = serializers.BooleanField(default=False, help_text="Show own products or not")
    search = serializers.CharField(allow_blank=True, required=False, help_text="Search query")
    min_price = serializers.DecimalField(required=False, min_value=0, max_digits=10, decimal_places=2)
    max_price = serializers.DecimalField(required=False, min_value=0, max_digits=10, decimal_places=2)
    model = serializers.CharField(required=False)

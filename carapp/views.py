from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from django.db import transaction
from .serializers import *
from rest_framework.exceptions import PermissionDenied
import logging
from django.db.models import Q
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from .serializers import CarUpdateSerializer, CarSerializer
from utils.tokens import get_user_id_from_token

logger = logging.getLogger('carapp.views')


class ProductDetail(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get_object(self, _id):
        try:
            user_id = get_user_id_from_token(self.request)
            user_profile = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return get_object_or_404(Car, id=_id)
        return get_object_or_404(Car, id=_id, user=user_profile)

    @transaction.atomic
    def get(self, request, _id):
        try:
            product = self.get_object(_id)
        except Http404:
            logger.error(f"Car with ID {_id} not found.")
            return Response({"message": f"Car Not Found"}, status=404)

        serializer = CarSerializer(product)
        product.views += 1
        product.save()
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer <token>",
                              type=openapi.TYPE_STRING),
        ],
        request_body=CarUpdateSerializer,
    )
    def put(self, request, _id):
        product = self.get_object(_id)
        serializer = CarUpDateNewSerializer(product, data=request.data, partial=True)

        if serializer.is_valid():
            cover_imgs = request.data.get('cover_img')

            # Удаляем старые изображения перед добавлением новых
            product.images.all().delete()

            if cover_imgs:
                for cover_img in cover_imgs:
                    CarImage.objects.create(product=product, image=cover_img)

            serializer.validated_data["model"] = product.category
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer <token>",
                              type=openapi.TYPE_STRING),
        ], )
    def delete(self, request, _id):
        try:
            product = self.get_object(_id)
            logger.info(f"Attempting to delete product with ID {_id}.")
        except Http404:
            logger.warning(f"Failed to delete product. Car with ID {_id} not found.")
            return Response({"message": "Car Not Found"}, status=404)

        user_id = get_user_id_from_token(request)
        user_profile = UserProfile.objects.get(id=user_id)

        if not product.is_deleted and user_profile.is_admin:
            product.is_deleted = True
            product.save()
            logger.info(f"Car with ID {_id} marked as deleted.")
            return Response({"message": "The product has been successfully removed"}, status=200)
        else:
            logger.warning(
                f"Failed to delete product. Car with ID {_id} has already been deleted or user is not an admin.")
            return Response({"message": "Car has already been deleted or unauthorized access."}, status=404)


class ProductList(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer <token>",
                              type=openapi.TYPE_STRING),
        ],
        query_serializer=CarQuerySerializer(),
    )
    def get(self, request):
        query_serializer = CarQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        show_own_products = query_serializer.validated_data.get('show_own_products', False)
        search_query = query_serializer.validated_data.get('search', None)
        min_price = query_serializer.validated_data.get('min_price')
        max_price = query_serializer.validated_data.get('max_price')
        categories = query_serializer.validated_data.get('model')

        try:
            user_id = get_user_id_from_token(request)
            user_profile = UserProfile.objects.get(id=user_id)
            if 2 + 2 == 4:
                products = Car.objects.filter(is_deleted=False, amount__gt=0)
            if user_profile.is_admin and not show_own_products:
                products = products.filter(is_deleted=False, amount__gt=0)
            elif user_profile.is_admin and show_own_products:
                products = products.filter(user=user_profile, is_deleted=False, amount__gt=0)

            if search_query:
                products = products.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

            if min_price is not None:
                products = products.filter(price__gte=min_price)
            if max_price is not None:
                products = products.filter(price__lte=max_price)
            if categories:
                try:
                    category = Model.objects.get(id=categories)
                    products = products.filter(category=category)
                except Model.DoesNotExist:
                    return Response({"message": "Model not found"}, status=404)

            products = products.order_by('-views')[:30]
            serializer = CarSerializer(products, many=True)

            return Response(serializer.data, status=200)

        except UserProfile.DoesNotExist:
            products = Car.objects.filter(is_deleted=False)

            if search_query:
                products = products.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

            if min_price is not None:
                products = products.filter(price__gte=min_price)
            if max_price is not None:
                products = products.filter(price__lte=max_price)
            if categories:
                try:
                    category = Model.objects.get(id=categories)
                    products = products.filter(category=category)
                except Model.DoesNotExist:
                    return Response({"message": "Model not found"}, status=404)

            products = products.order_by('-views')[:30]
            serializer = CarSerializer(products, many=True)
            return Response(serializer.data, status=200)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer <token>",
                              type=openapi.TYPE_STRING),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'model': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID of the model"),
                'title': openapi.Schema(type=openapi.TYPE_STRING, description="Title of the item"),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description="Description of the item"),
                'price': openapi.Schema(type=openapi.TYPE_INTEGER, description="Price of the item"),
                'amount': openapi.Schema(type=openapi.TYPE_INTEGER, description="Amount of the item"),
                'default_account': openapi.Schema(type=openapi.TYPE_INTEGER, description="Default account for money")
            },
            required=['model', 'title', 'description', 'price', 'amount']
        ),
        security=[],
    )
    @transaction.atomic
    def post(self, request):
        try:
            # Get the array of images from the request data
            cover_imgs = request.data.get('cover_img')
            if cover_imgs:
                pass
            else:
                cover_imgs = []
            # Get the user profile based on the token or however you identify the user
            user_id = get_user_id_from_token(request)
            user_profile = UserProfile.objects.get(id=user_id)

            # Check if the user is an admin
            if not user_profile.is_admin:
                raise PermissionDenied("You don't have permission to create a product.")
            if not Account.objects.filter(user=user_profile).first():
                raise PermissionDenied("You are have not account please create account and replay.")

            data = {
                'user': user_profile,
                'model': request.data.get('model'),
                'title': request.data.get('title'),
                'description': request.data.get('description'),
                'price': request.data.get('price'),
                'amount': request.data.get('amount'),
                'default_account': request.data.get('default_account')
            }

            # Log request data
            logger.info(f"Request data - User: {user_profile.username}, Data: {data}, Cover Images: {cover_imgs}")

            # Create a CarSerializer instance with the data and cover_imgs
            try:
                account = Account.objects.filter(user=user_profile).first()
                if account:
                    if data["default_account"] is None:
                        data["default_account"] = account.id
                    else:
                        try:
                            account = Account.objects.get(id=data["default_account"], user=user_profile)
                        except Account.DoesNotExist:
                            user_id = get_user_id_from_token(request)
                            logger.warning(
                                f"Failed to retrieve products for user with ID {user_id}. Account Not Found.")
                            data["default_account"] = account.id
            except Account.DoesNotExist:
                user_id = get_user_id_from_token(request)
                logger.warning(f"Failed to create product for user with ID {user_id}. Account Not Found.")
                return Response({"warning": "You are have not account please create account and replay."},
                                status=status.HTTP_404_NOT_FOUND)
            serializer = CarSerializer(data=data)
            if serializer.is_valid():
                # Save the product instance
                product = serializer.save()

                # Save each image in the cover_imgs array
                for cover_img in cover_imgs:
                    CarImage.objects.create(product=product, image=cover_img)

                # Log information including user details, product ID, and image details
                logger.info(
                    f"Car created successfully. User: {user_profile.username}, Car ID: {product.id}, Cover "
                    f"Images: {cover_imgs}")

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Invalid data provided: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied as pd:
            logger.warning("Permission Denied: " + str(pd) + "")
            return Response({"Permission Denied": str(pd)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductUser(APIView):
    def get(self, request, user_id):
        try:
            user_profile = UserProfile.objects.get(id=user_id)
            products = Car.objects.filter(user=user_profile)

            if not products.exists():
                return Response({"message": f"No products found for the user with id {user_id}"},
                                status=status.HTTP_404_NOT_FOUND)

            serializer = CarSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            logger.warning(f"Failed to get user profile. User profile not found.")
            return Response({"message": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"An error occurred while processing the request: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


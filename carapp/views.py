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


class CarDetail(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [AllowAny]

    def get_object(self, _id):
        try:
            user_id = get_user_id_from_token(self.request)
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return get_object_or_404(Car, id=_id)
        return get_object_or_404(Car, id=_id, user=user)

    @transaction.atomic
    def get(self, request, _id):
        try:
            car = self.get_object(_id)
        except Http404:
            logger.error(f"Car with ID {_id} not found.")
            return Response({"message": f"Car Not Found"}, status=404)

        serializer = CarSerializer(car)
        car.views += 1
        car.save()
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Bearer <token>",
                              type=openapi.TYPE_STRING),
        ],
        request_body=CarUpdateSerializer,
    )
    def put(self, request, _id):
        car = self.get_object(_id)
        serializer = CarUpdateSerializer(car, data=request.data, partial=True)

        if serializer.is_valid():
            cover_imgs = request.data.get('cover_img')

            # Удаляем старые изображения перед добавлением новых
            car.images.all().delete()

            if cover_imgs:
                for cover_img in cover_imgs:
                    CarImage.objects.create(car=car, image=cover_img)

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
            car = self.get_object(_id)
            logger.info(f"Attempting to delete car with ID {_id}.")
        except Http404:
            logger.warning(f"Failed to delete car. Car with ID {_id} not found.")
            return Response({"message": "Car Not Found"}, status=404)

        user_id = get_user_id_from_token(request)
        user = UserProfile.objects.get(id=user_id)

        if not car.is_deleted and user.is_superuser:
            car.is_deleted = True
            car.save()
            logger.info(f"Car with ID {_id} marked as deleted.")
            return Response({"message": "The car has been successfully removed"}, status=200)
        else:
            logger.warning(
                f"Failed to delete car. Car with ID {_id} has already been deleted or user is not a superuser.")
            return Response({"message": "Car has already been deleted or unauthorized access."}, status=404)


class CarList(APIView):
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
        model = query_serializer.validated_data.get('model')

        try:
            user_id = get_user_id_from_token(request)
            user = UserProfile.objects.get(id=user_id)

            cars = Car.objects.filter(is_deleted=False)

            if search_query:
                cars = cars.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

            if min_price is not None:
                cars = cars.filter(price__gte=min_price)
            if max_price is not None:
                cars = cars.filter(price__lte=max_price)
            if model:
                try:
                    model_obj = Model.objects.get(id=model)
                    cars = cars.filter(model=model_obj)
                except Model.DoesNotExist:
                    return Response({"message": "Model not found"}, status=404)

            cars = cars.order_by('-views')[:30]
            serializer = CarSerializer(cars, many=True)

            return Response(serializer.data, status=200)

        except UserProfile.DoesNotExist:
            cars = Car.objects.filter(is_deleted=False)

            if search_query:
                cars = cars.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))

            if min_price is not None:
                cars = cars.filter(price__gte=min_price)
            if max_price is not None:
                cars = cars.filter(price__lte=max_price)
            if model:
                try:
                    model_obj = Model.objects.get(id=model)
                    cars = cars.filter(model=model_obj)
                except Model.DoesNotExist:
                    return Response({"message": "Model not found"}, status=404)

            cars = cars.order_by('-views')[:30]
            serializer = CarSerializer(cars, many=True)
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
                'price': openapi.Schema(type=openapi.TYPE_NUMBER, description="Price of the item"),
                'amount': openapi.Schema(type=openapi.TYPE_INTEGER, description="Amount of the item"),
                'cover_img': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                            description="Array of image URLs")
            },
            required=['model', 'title', 'description', 'price', 'amount']
        ),
        security=[],
    )
    @transaction.atomic
    def post(self, request):
        try:
            # Get the array of images from the request data
            cover_imgs = request.data.get('cover_img') or []

            # Get the user profile based on the token or however you identify the user
            user_id = get_user_id_from_token(request)
            user = UserProfile.objects.get(id=user_id)

            # Check if the user is an admin or has permissions to create a car
            if not user.is_superuser:
                raise PermissionDenied("You don't have permission to create a car.")

            data = {
                'user': user,
                'model': request.data.get('model'),
                'title': request.data.get('title'),
                'description': request.data.get('description'),
                'price': request.data.get('price'),
                'amount': request.data.get('amount'),
            }

            # Log request data
            logger.info(f"Request data - User: {user.username}, Data: {data}, Cover Images: {cover_imgs}")

            # Create a CarSerializer instance with the data and cover_imgs
            serializer = CarSerializer(data=data)
            if serializer.is_valid():
                # Save the car instance
                car = serializer.save()

                # Save each image in the cover_imgs array
                for cover_img in cover_imgs:
                    CarImage.objects.create(car=car, image=cover_img)

                # Log information including user details, car ID, and image details
                logger.info(
                    f"Car created successfully. User: {user.username}, Car ID: {car.id}, Cover Images: {cover_imgs}")

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Invalid data provided: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except PermissionDenied as pd:
            logger.warning("Permission Denied: " + str(pd))
            return Response({"Permission Denied": str(pd)}, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            logger.error("User not found")
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CarUser(APIView):
    def get(self, request, user_id):
        try:
            user = UserProfile.objects.get(id=user_id)
            cars = Car.objects.filter(user=user)

            if not cars.exists():
                return Response({"message": f"No cars found for the user with id {user_id}"},
                                status=status.HTTP_404_NOT_FOUND)

            serializer = CarSerializer(cars, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            logger.error(f"User with ID {user_id} does not exist.")
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"An error occurred while processing the request: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

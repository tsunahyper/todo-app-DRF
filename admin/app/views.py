from .models import Todo
from .serializer import TodoSerializer,UserRegisterSerializer

from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)# Obtain a token pair when a user logs in
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.status import HTTP_201_CREATED,HTTP_400_BAD_REQUEST

# Create a token pair when a user logs in
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        response = super().post(request, *args, **kwargs)  # Get token pair using parent method, super() allows us to use methods from TokenObtainPairView and post() method in TokenObtainPairView is responsible for handling the token generation when a user logs in
        tokens = response.data  # Fetch the tokens from the response data
        
        # Ensure and fetch the access_token and refresh_token exist in the response
        access_token = tokens.get('access')
        refresh_token = tokens.get('refresh')

        # If both tokens are successfully created, proceed to set them in cookies
        if access_token and refresh_token:
            res = Response({'success': True}, status=200)  # Response to return to the client
            # Set the access token in a secure HTTP-only cookie
            res.set_cookie(key='access_token', value=access_token, httponly=True, secure=True, samesite=None, path='/')
            # Set the refresh token in a secure HTTP-only cookie
            res.set_cookie(key='refresh_token', value=refresh_token, httponly=True, secure=True, samesite=None, path='/')
            
            return res
        else:
            # Handle the case where the tokens could not be created (e.g., invalid credentials)
            return Response({
                'success': False,
                'message': 'Unable to create tokens. Please check your credentials.'
            }, status=400)

# Create a custom refresh token that refreshes the access token without having user to reauthenticate and logged in
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        try:
            # Fetch the refresh token from the request cookies
            refresh_token = request.COOKIES.get('refresh_token')
            # Assign the refresh token to the payload
            request.data['refresh'] = refresh_token

            # Call the parent method to handle the token refresh process
            response = super().post(request, *args, **kwargs)
            tokens = response.data  # Get new tokens from the response
            access_token = tokens.get('access')  # Extract the new access token

            # Set the access token in a secure HTTP-only cookie
            res = Response({'refresh_token': True})  # Success response
            res.set_cookie(key='access_token', value=access_token, httponly=True, secure=True, samesite=None, path='/')
            return res  # Return response with updated access token
        except:
            # Handle any exception that occurs during the refresh process
            return Response({
                'success': False,
                'message': 'Unable to generate a new access token. Kindly check the refresh token.'
            }, status=400)  # Return error response


# Logout view that deletes tokens stored in cookies
@api_view(['POST'])
def logout(request):
    try:
        res = Response({'success': True})  # Success response
        # Delete the access_token and refresh_token cookies
        res.delete_cookie('access_token', path='/')
        res.delete_cookie('refresh_token', path='/')
        return res  # Return response with cookies deleted
    except:
        # Handle any exception that occurs during logout
        return Response({
            'success': False,
            'message': 'Unable to delete tokens. Error occurred!'
        }, status=400)  # Return error response


# User registration view
@api_view(['POST'])
@permission_classes([AllowAny])  # Allow any user (authenticated or not) to access this API
def register(request):
    serializer = UserRegisterSerializer(data=request.data)  # Use serializer to validate user data
    # Check if the serializer is valid
    if serializer.is_valid():
        serializer.save()  # Save the user if the data is valid
        return Response(serializer.data, status=201)  # Return the saved data with a 201 Created status
    # If the serializer is not valid, return specific validation errors
    return Response({
        'success': False, 
        'Error': serializer.errors  # Return validation errors
    }, status=400)  # Bad request
    

class TodoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # Allow only authenticated users
    serializer_class = TodoSerializer

    def get_queryset(self):
        user = self.request.user # Get the currently logged-in user
        # Return todos for the logged-in user
        return Todo.objects.filter(user=user) 

    # Custom action for searching todos by title
    @action(detail=False, methods=['GET'], url_path="search")
    def search_todos(self, request):
        search_param = request.GET.get("title", None)  # Get the search query from URL params
        if search_param:
            # Filter todos by title containing the search_param (case-insensitive)
            todos = self.get_queryset().filter(title__icontains=search_param) # Get a dataset based on the search parameters that contains a word from the title
            serializer = TodoSerializer(todos, many=True) # Set to many incoming datas
            return Response(serializer.data)  # Return serialized todo data
        return Response({"message": "No search parameter provided"}, status=400)
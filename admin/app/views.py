from .models import Todo
from .serializer import TodoSerializer,UserRegisterSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Obtain a token pair when a user logs in
    TokenRefreshView,
)
from django.shortcuts import get_object_or_404


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


# View to verify if the user is authenticated
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Only if the user is authenticated can they access this API
def user_authenticate(request):
    return Response({'authenticate_success': True}, status=200)  # Return success response if authenticated


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


# Get all todos for the authenticated user
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Only if user is authenticated, can they access this API
def get_todos(request):
    user = request.user  # Get the logged-in user
    todos = Todo.objects.filter(user=user)  # Filter todos that belong to the user
    serializer = TodoSerializer(todos, many=True)  # Serialize the todos
    return Response(serializer.data)  # Return serialized data


# Create a new todo item for the authenticated user
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Only if user is authenticated, can they access this API
def create_todos(request):
    user = request.user  # Get the logged-in user
    data = request.data  # Get the request data

    # Add the user to the data so the todo is associated with the logged-in user
    data['user'] = user.id

    # Use the serializer to validate the data and save it to the database
    serializer = TodoSerializer(data=data)
    
    if serializer.is_valid():  # Check if the data is valid
        serializer.save()  # Save the valid data to the database
        return Response(serializer.data, status=201)  # Return the saved data with a 201 Created status
    else:
        return Response(serializer.errors, status=400)  # Return validation errors if any


# Update a todo item for the authenticated user
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])  # Only authenticated users can update todos
def update_todos(request, todo_id):
    user = request.user  # Get the currently logged-in user
    todo = get_object_or_404(Todo, id=todo_id, user=user)  # Ensure the todo exists and belongs to the user
    
    # If the todo exists, update it
    if todo:
        data = request.data  # Get the data from the request
        # Use the serializer to validate the updated data
        serializer = TodoSerializer(todo, data=data, partial=True)  # `partial=True` allows partial updates
        
        if serializer.is_valid():  # Check if the data is valid
            serializer.save()  # Save the updated data
            return Response(serializer.data, status=200)  # Return the updated data with a 200 OK status
        else:
            return Response(serializer.errors, status=400)  # Return validation errors if any
    
    # If no todo exists, return an error message
    return Response({'Message':'Data is empty, there is no todo notes created in the list'})  # Return error message


# Delete a todo item for the authenticated user
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])  # Only authenticated users can delete todos
def delete_todos(request, todo_id):
    user = request.user  # Get the currently logged-in user
    todo = get_object_or_404(Todo, id=todo_id, user=user)  # Ensure the todo exists and belongs to the user
    
    todo.delete()  # Delete the todo
    return Response({'message': 'Todo deleted successfully!'}, status=204)  # Return 204 No Content status after deletion
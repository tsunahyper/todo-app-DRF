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
        response = super().post(request, *args, **kwargs)  # Get token pair
        tokens = response.data
        
        # Ensure access_token and refresh_token exist in the response
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
            refresh_token = request.COOKIES.get('refresh_token')
            request.data['refresh'] = refresh_token
            response = super().post(request, *args, **kwargs)
            tokens = response.data
            access_token = tokens.get('access')

            res = Response()

            res.data = {
                'refresh_token': True
            }
            res.set_cookie(key='access_token', value=access_token, httponly=True, secure=True, samesite=None, path='/')
            return res
        except:
            # Handle the case where the tokens could not be created (e.g., invalid credentials)
            return Response({
                'success': False,
                'message': 'Unable to generate a new access tokens. Kindly check the refresh token.'
            }, status=400)


@api_view(['POST'])
def logout(request):
    try:
        res = Response()
        res.data = {
            'success': True
        }
        res.delete_cookie('access_token', path='/')
        res.delete_cookie('refresh_token', path='/')
        return res
    except:
        return Response({
                'success': False,
                'message': 'Unable to delete tokens. Error occured!'
            }, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated]) # Only if user authenticated, can they access this API
def user_authenticate(request):
    return Response({
        'authenticate_success': True
    }, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow any user to access this API
def register(request):
    serializer = UserRegisterSerializer(data=request.data)
    
    # Check if the serializer is valid
    if serializer.is_valid():
        # Save the user if the data is valid
        serializer.save()
        return Response(serializer.data, status=201)  # Success response
    
    # If the serializer is not valid, return the specific errors
    return Response({
        'success': False, 
        'Error': serializer.errors  # Return specific validation errors
    }, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) # Only if user authenticated, can they access this API
def get_todos(request):
    user = request.user
    todos = Todo.objects.filter(user=user)
    serializer = TodoSerializer(todos, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated]) # Only if user authenticated, can they access this API
def create_todos(request):
    user = request.user
    data = request.data
    
    # Add the user to the data so the todo is associated with the logged-in user
    data['user'] = user.id

    # Use the serializer to validate the data and save it to the database
    serializer = TodoSerializer(data=data)
    
    if serializer.is_valid():  # Check if the data is valid
        serializer.save()  # Save the valid data to the database
        return Response(serializer.data, status=201)  # Return the saved data with a status of 201 (created)
    else:
        return Response(serializer.errors, status=400)  # Return validation errors if any


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])  # Only authenticated users can update todos
def update_todos(request, todo_id):
    user = request.user  # Get the currently logged-in user
    todo = get_object_or_404(Todo, id=todo_id, user=user)  # Ensure the todo exists and belongs to the user
    print(todo)
    if todo:
        # Get the data from the request (either full update with PUT or partial with PATCH)
        data = request.data

        # Use the serializer to validate the updated data
        serializer = TodoSerializer(todo, data=data, partial=True)  # `partial=True` allows partial updates
        
        if serializer.is_valid():  # Check if the data is valid
            serializer.save()  # Save the updated data
            return Response(serializer.data, status=200)  # Return the updated data with a status of 200 (OK)
        else:
            return Response(serializer.errors, status=400)  # Return validation errors if any
    return Response({'Message':'Data is empty, there is no todo notes created in the list'})  # Return validation errors if any


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])  # Only authenticated users can delete todos
def delete_todos(request, todo_id):
    user = request.user  # Get the currently logged-in user
    todo = get_object_or_404(Todo, id=todo_id, user=user)  # Ensure the todo exists and belongs to the user
    
    todo.delete()  # Delete the todo
    return Response({'message': 'Todo deleted successfully!'}, status=204)  # 204 status code indicates no content

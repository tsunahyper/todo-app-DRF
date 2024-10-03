from django.urls import path,re_path
from .views import get_todos,logout,user_authenticate,register,create_todos,update_todos,delete_todos,CustomTokenObtainPairView,CustomTokenRefreshView

urlpatterns = [
    # Generate and Refresh JWT token endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    # User CRUD methods for Todo Features
    path('todo/', get_todos, name='todo'),
    path('todo/create/', create_todos, name='todo_create'),
    path('todo/update/<int:todo_id>/', update_todos, name='todo_update'),
    path('todo/delete/<int:todo_id>/', delete_todos, name='todo_delete'),

    # User Authentication, Login, Register Features
    path('register/', register, name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', logout, name='logout'),
    path('authenticate/', user_authenticate, name='authenticate_user'),
]
# Todo App with JWT Authentication (Django Rest Framework)

This is a **Todo App** built using Django REST Framework. It includes full **CRUD** functionalities for managing todos and incorporates **JWT (JSON Web Token) authentication** for user login, registration, and securing the API endpoints. The application has no frontend interface but can be tested and viewed using **Django REST Framework's browsable API**.

## Features

1. **User Authentication:**
   - Users can **register**, **login**, and **logout** using the API.
   - Passwords are securely stored using Django’s built-in `User` model.
   - JWT is used to secure the login and authentication process. Upon successful login, an **access token** and **refresh token** are generated.

2. **JWT Token-Based Authentication:**
   - The app uses **JWT** to authenticate users and protect the endpoints. 
   - JWT tokens are passed in HTTP-only cookies to securely authenticate each request.
   - Access tokens have a short lifespan (e.g., 5 minutes), while refresh tokens are used to generate new access tokens without needing to log in again.

3. **Todo CRUD Features:**
   - Users can **Create**, **Read**, **Update**, and **Delete** (CRUD) their own todos.
   - Each user has access only to their own todos (ensured through the authentication system).

4. **Django REST Framework Interface:**
   - The app does not have a custom frontend but uses **Django REST Framework**'s browsable API.
   - You can interact with the app directly by making API requests through a tool like Postman or by browsing the API through Django’s built-in interface.

## Endpoints

### Authentication

1. **Register:**
   - **POST** `/api/register/` - Register a new user.
   - Request payload:
     ```json
     {
       "username": "zack",
       "email": "zack@gmail.com",
       "password": "password123"
     }
     ```

2. **Login:**
   - **POST** `/api/login/` - Login a user and receive JWT tokens (access & refresh).
   - Request payload:
     ```json
     {
       "username": "zack",
       "password": "password123"
     }
     ```
   - The response will include `access_token` and `refresh_token`, stored in HTTP-only cookies.

3. **Token Refresh:**
   - **POST** `/api/token/refresh/` - Refresh the access token using the refresh token.

4. **Logout:**
   - **POST** `/api/logout/` - Log out the user and invalidate the tokens.

### Todo Management (Requires Authentication)

1. **Get All Todos:**
   - **GET** `/api/todo/` - Retrieve all todos for the authenticated user.
   
2. **Create Todo:**
   - **POST** `/api/todo/` - Create a new todo.
   - Sample Request payload:
     ```json
     {
       "title": "Finish Django project",
       "description": "Complete the remaining features of the app."
       "user": <user pk id>
     }
     ```

3. **Update Todo:**
   - **PUT** `/api/todo/<todo_id>/` - Update an existing todo.
   - Sample Request payload:
     ```json
     {
       "title": "Todo 2",
       "description": "Updated todo via API",
       "user": <user pk id>
     }
     ```

4. **Delete Todo:**
   - **DELETE** `/api/todo/<todo_id>/` - Delete a todo.

## How to Use

- Clone the repository to your local machine.
- Set up a virtual environment and install the required dependencies listed in `requirements.txt`.
- Run database migrations using:
  ```bash
  python manage.py migrate
- You can now use the Django REST Framework API interface to test the app’s features by navigating to http://127.0.0.1:8000/api/ in your browser.

Requirements Needed for building the Django Todo App:

	•	Python 3.x
	•	Django 5.x
	•	Django REST Framework
	•	Django SimpleJWT
	•	Other dependencies listed in requirements.txt

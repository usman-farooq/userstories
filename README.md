# User stories server
Python Django API server to manage user stories

# How to run the server
Access the server APIs at http://ec2-34-212-94-107.us-west-2.compute.amazonaws.com

Note: APIs are using authentication token instead of session based login so get `token` from `/auth-token` API and pass to subsequent API calls as Authorization header

Sample user: 
- username: admin@example.com
- password: useruser

# Technical Choices

* Languages and frameworks: Python3, Django 2.2.1, django restframework 3.10
* API Authentication: rest_framewrok Token Authentication

# API documentation

* POST: `/auth-token` takes `username` (email) and `password` as request data and returns `token` to use in subsequent API calls
* POST: `/resources` takes `content` as request data and `token` as Authorization header (`Authorization: Token <token>`). This API creates new resource in database with unique id
* GET: `/resources` takes user token as Authorization header and returns all resources for that user or if user is adminstrator then returns resources of all users
* DELETE `/resources/<resource_id>` takes token as Authorization header and resource id (to be deleted) as path parameter. This API deletes resource against provided resource id

* POST: `/users` creates new user with request data based on parameters; `email`, `password`, `is_superuser`, `quota`. Only administrator can access this API and it requires user token as Authorization header
* GET: `/users` takes user token as Authorization header and returns all users
* PUT: `/users/<email>` requires user token and `quota` as request parameter and updates user's resources quota. Target user's email is expected to pass as path parameter 
* DELETE: `/users/<email>` requires user token and takes target user email as path parameter to delete the user against provided email

# Expected API errors

* POST: `/auth-token` 400 Bad Request - if user credentials are incorrect
* POST: `/users` 400 Bad Request - if request data is not provided
* GET: `/users` 401 Unauthorized - if user token is invalid or user don't have permissions to access the API
* POST `/resources` 406 Not Acceptable - if user's resources quota has reached the limit
* GET `/resources/<resource_id>` 404 Not Found - if resource does not exist against provided resource id

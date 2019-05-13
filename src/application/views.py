from application import serializers
from application.models import User, Resource
from application.permissions import IsAuthenticated, IsSuperUser, IsOwnerOrSuperUser
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework import status

'''
User main class to get all user or to create a new user
Note: Only supper user can get or create new users
'''
class UserMainView(ListCreateAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = (IsSuperUser,)
    
    def get_queryset(self):
        users = User.objects.all()
        return users
    
    # Get all users
    def get(self, request):
        users = self.get_queryset()
        serializer = self.serializer_class(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Create new user 
    def post(self, request):
        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

'''
User class to get, update or delete user based on provided user email address
Note: Only supper user can access user class methods
'''
class UserObjectView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated, IsSuperUser,)
    
    def get_queryset(self, email):
        return get_object_or_404(User, email=email)
    
    # Get user by email
    def get(self, request, email):
        user = self.get_queryset(email)
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Update user quota
    def put(self, request, email):
        user = self.get_queryset(email)
        user.quota = request.data['quota']
        user.save()
        serializer = serializers.UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Delete user by email
    def delete(self, request, email):
        user = self.get_queryset(email)
        user.delete()
        content = {'status': 'OK'}
        return Response(content, status=status.HTTP_200_OK)

'''
Resources Class
1. To get all resources of logged in user or if user is super user then 
all resources belongs to any user will be returned.
2. Post a new resources against logged in user
'''
class ResourceMainView(ListCreateAPIView):
    serializer_class = serializers.ResourceSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrSuperUser,)
    
    def get_queryset(self):
        resources = Resource.objects.all()
        if self.request.user.is_superuser:
            return resources
        return resources.filter(created_by=self.request.user)

    # Get all resources
    def get(self, request):
        resources = self.get_queryset()
        serializer = self.serializer_class(resources, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Create a new resource
    def post(self, request):
        serializer = serializers.ResourceSerializer(data=request.data)
        
        if serializer.is_valid():
            quota = self.request.user.quota
            # Check if user quota is set then make sure quota is not already full
            if quota is not None and quota <= self.get_queryset().count():
                content = {'status': 'Resources quota exceeded'}
                return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
            
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
'''
Resources class to get or delete resources based on provided resource id
'''
class ResourceObjectView(RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.ResourceSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrSuperUser,)
    
    def get_queryset(self, resource_id):
        try: return Resource.objects.get(pk=resource_id)
        except Resource.DoesNotExist:
            content = {'status': 'Not Found'}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
    
    # Get resource by id
    def get(self, request, resource_id):
        resource = self.get_queryset(resource_id)
        serializer = serializers.ResourceSerializer(resource)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Delete resource by id
    def delete(self, request, resource_id):
        resource = self.get_queryset(resource_id)
        resource.delete()
        content = {'status': 'OK'}
        return Response(content, status=status.HTTP_200_OK)

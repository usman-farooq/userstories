'''
Created on May 12, 2019

@author: usman.farooq
'''
from rest_framework import serializers
from application.models import User, Resource


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'is_superuser', 'quota')
    
    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data.get('password'))
        user.save()
        return user

class ResourceSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.email')
    
    class Meta:
        model = Resource
        fields = ('id', 'content', 'created_by')

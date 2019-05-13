import json
from django.test import TestCase, Client

from application.models import User

class UserAPITests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_superuser(email='test@example.com', password='superuser')
        self.user.is_superuser = True
        self.user.save()
        self.client = Client(content_type='application/json')
         
        response = self.client.post('/auth-token', dict(username='test@example.com', password='superuser'))
        auth_token = json.loads(response.content).get('token')
        
        '''Superuser authentication token that will be used in API testing'''
        self.auth_header = {'HTTP_AUTHORIZATION': 'Token ' + auth_token}
        
    def test_get_users(self):
        response = self.client.get('/users', **self.auth_header)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), 1)
        self.assertIsNone(content[0].get('quota'))
        self.assertTrue(content[0].get('is_superuser'))
        self.assertEqual(content[0].get('email'), self.user.email)
     
    def test_create_delete_user(self):
        # Create new user (non-super)
        data = {'email': 'test2@example.com', 'password': 'useruser'}
        response = self.client.post('/users', data, **self.auth_header)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(content.get('quota'))
        self.assertEqual(content.get('email'), data.get('email'))
         
        # Delete user
        response = self.client.delete('/users/test2@example.com', **self.auth_header)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
     
    def test_update_user_quota(self):
        data = {'quota': '30'}
        response = self.client.put('/users/test@example.com', data, 'application/json', **self.auth_header)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content.get('quota'), 30)
        self.assertEqual(content.get('email'), self.user.email)
    
        
class ResourceAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(email='test@example.com', password='superuser')
        self.user.is_superuser = True
        self.user.save()
        self.client = Client(content_type='application/json')
        
        response = self.client.post('/auth-token', dict(username='test@example.com', password='superuser'))
        auth_token = json.loads(response.content).get('token')
        self.auth_header = {'HTTP_AUTHORIZATION': 'Token ' + auth_token}
    
    def create_resource(self, content, auth_header=None):
        data = {'content': content}
        if not auth_header: auth_header = self.auth_header
        response = self.client.post('/resources', data, **auth_header)
        return response
        
    def test_post_resource(self):
        response = self.create_resource('user story content')
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(content.get('id'), 1)
        self.assertEqual(content.get('content'), 'user story content')
        self.assertEqual(content.get('created_by'), self.user.email)
        
    def test_delete_resource(self):
        response = self.create_resource('user story sample content')
        content = json.loads(response.content)
        
        response = self.client.delete('/resources/'+str(content.get('id')), **self.auth_header)
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
         
    def test_get_all_resources(self):
        resources = []
        for i in range(3):
            resource = json.loads(self.create_resource('content ' + str(i)).content)
            resources.append(resource)
         
        response = self.client.get('/resources', **self.auth_header)
        content = json.loads(response.content)
         
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), len(resources))
    
    def test_get_user_resources(self):
        # First create new non-super user
        user = User.objects.create_user(email='tester@example.com', password='useruser')
        user.save()
        
        superuser = User.objects.create_superuser(email='admin@example.com', password='superuser')
        superuser.is_superuser = True
        superuser.save()
        
        # Get auth token required to post new resource
        user_client = Client(content_type='application/json')
        data = {'username': 'tester@example.com', 'password': 'useruser'}
        response = user_client.post('/auth-token', data)
        user_token = json.loads(response.content).get('token')
        user_auth_header = {'HTTP_AUTHORIZATION': 'Token ' + user_token}
        
        # Get auth token required to post new resource
        admin_client = Client(content_type='application/json')
        admin_data = {'username': 'admin@example.com', 'password': 'superuser'}
        admin_response = admin_client.post('/auth-token', admin_data)
        admin_token = json.loads(admin_response.content).get('token')
        admin_auth_header = {'HTTP_AUTHORIZATION': 'Token ' + admin_token}
        
        user_resources = []
        for i in range(3):
            data = {'content': 'user story content' + str(i)}
            response = user_client.post('/resources', data, **user_auth_header)
            content = json.loads(response.content)
            user_resources.append(content)
        
        admin_resources = []
        for i in range(3):
            data = {'content': 'admin story content' + str(i)}
            response = admin_client.post('/resources', data, **admin_auth_header)
            content = json.loads(response.content)
            admin_resources.append(content)
        
        # Get all resources of non-super user
        response = user_client.get('/resources', **user_auth_header)
        content = json.loads(response.content)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), len(user_resources))
        
        # Get all resources by super user
        response = admin_client.get('/resources', **admin_auth_header)
        content = json.loads(response.content)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(content), len(user_resources + admin_resources))
        
        
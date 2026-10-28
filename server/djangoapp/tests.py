import json
from unittest.mock import patch
import requests
from django.test import TestCase
from django.contrib.auth.models import User

class AccountAndReviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('reviewer', password='Test-only!Password42', first_name='Test', last_name='Reviewer')
    def post(self, path, data):
        return self.client.post('/djangoapp/'+path, json.dumps(data), content_type='application/json')
    def test_login_logout_session(self):
        self.assertEqual(self.post('login', {'userName':'reviewer','password':'wrong'}).status_code,401)
        self.assertEqual(self.post('login', {'userName':'reviewer','password':'Test-only!Password42'}).status_code,200)
        self.assertEqual(self.client.get('/djangoapp/user').json()['userName'],'reviewer')
        self.post('logout',{})
        self.assertIsNone(self.client.get('/djangoapp/user').json()['userName'])
    def test_registration_and_duplicate(self):
        data={'username':'newperson','first_name':'New','last_name':'Person','email':'person@example.com','password':'Test-only!Secure56'}
        self.assertEqual(self.post('register',data).status_code,201)
        self.assertEqual(self.post('register',data).status_code,409)
        self.assertNotEqual(User.objects.get(username='newperson').password,data['password'])
    def test_bad_registration_and_json(self):
        self.assertEqual(self.post('register',{'username':'x'}).status_code,400)
        self.assertEqual(self.client.post('/djangoapp/login','{',content_type='application/json').status_code,400)
    @patch('djangoapp.restapis.post_review',return_value={'id':100})
    def test_reviews_require_auth_and_use_server_identity(self, upstream):
        data={'dealership':1,'review':'Helpful staff','car_year':2024,'name':'Forged identity'}
        self.assertEqual(self.post('add_review',data).status_code,401)
        self.client.force_login(self.user)
        self.assertEqual(self.post('add_review',data).status_code,201)
        self.assertEqual(upstream.call_args.args[0]['name'],'Test Reviewer')
        data['car_year']=1900
        self.assertEqual(self.post('add_review',data).status_code,400)
    @patch('djangoapp.restapis.get_request',side_effect=requests.ConnectionError())
    def test_backend_failure_is_actionable(self, upstream):
        self.assertEqual(self.client.get('/djangoapp/get_dealers').status_code,502)
    @patch('djangoapp.restapis.get_request',return_value=[{'id':1,'state':'Kansas'}])
    def test_state_filter_routes_to_backend(self, upstream):
        self.assertEqual(self.client.get('/djangoapp/get_dealers/Kansas').json()['dealers'][0]['state'],'Kansas')
        upstream.assert_called_once_with('fetchDealers/Kansas')
    def test_static_information_pages(self):
        self.assertContains(self.client.get('/about'),'Meet our team')
        self.assertContains(self.client.get('/contact'),'support@bestcars.example')

class LogoutCompatibilityTests(TestCase):
    def test_get_logout_clears_authenticated_session(self):
        user=User.objects.create_user('logout_fixture',password='TestOnly!2026')
        self.client.force_login(user)
        response=self.client.get('/djangoapp/logout')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['userName'],'')
        self.assertIsNone(self.client.get('/djangoapp/user').json()['userName'])

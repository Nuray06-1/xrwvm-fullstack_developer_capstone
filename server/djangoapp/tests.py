import json
from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import CarMake, CarModel

class PortalTests(TestCase):
    def setUp(self):
        make=CarMake.objects.create(name='Toyota')
        self.car=CarModel.objects.create(car_make=make,name='Camry',type='Sedan',year=2023)
    def post(self,path,data):
        return self.client.post('/djangoapp/'+path,json.dumps(data),content_type='application/json')
    def test_registration_login_logout(self):
        data={'userName':'driver','password':'RiverJourney!2049','firstName':'Demo'}
        self.assertEqual(self.post('register',data).status_code,201)
        self.assertEqual(self.client.get('/djangoapp/session').json()['userName'],'driver')
        self.assertEqual(self.post('logout',{}).status_code,200)
        self.assertIsNone(self.client.get('/djangoapp/session').json()['userName'])
        self.assertEqual(self.post('login',{**data,'password':'wrong'}).status_code,401)
        self.assertEqual(self.post('login',data).status_code,200)
    def test_password_validation(self):
        self.assertEqual(self.post('register',{'userName':'driver','password':'123'}).status_code,400)
        self.assertEqual(User.objects.count(),0)
    def test_review_requires_login(self):
        self.assertEqual(self.post('add_review',{}).status_code,401)
    def test_csrf_is_enforced(self):
        client=Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/djangoapp/login','{}',content_type='application/json').status_code,403)
    def test_malformed_input(self):
        self.assertEqual(self.client.post('/djangoapp/login','invalid',content_type='application/json').status_code,400)
    @patch('djangoapp.restapis.post_review',return_value={'id':100})
    @patch('djangoapp.restapis.get_request',return_value={'id':1})
    def test_review_uses_authenticated_author(self,get,post):
        user=User.objects.create_user('driver',password='RiverJourney!2049')
        self.client.force_login(user)
        data={'name':'Spoofed','review':'Helpful service!','dealership':1,'car_id':self.car.id,'purchase':True,'purchase_date':'2023-04-01'}
        self.assertEqual(self.post('add_review',data).status_code,201)
        self.assertEqual(post.call_args.args[0]['name'],'driver')
        self.assertEqual(self.post('add_review',{**data,'purchase_date':'2099-01-01'}).status_code,400)
    @patch('djangoapp.restapis.get_request',return_value=[])
    def test_state_filter(self,get):
        self.assertEqual(self.client.get('/djangoapp/get_dealers?state=Kansas').status_code,200)
        get.assert_called_once_with('fetchDealers/Kansas')
    def test_catalogue(self):
        self.assertEqual(self.client.get('/djangoapp/get_cars').json()['cars'][0]['car_make__name'],'Toyota')

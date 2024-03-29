import re
import unittest
from app import create_app, db
from app.models import User, Role



class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Stranger' in response.get_data(as_text=True))

    def test_register_and_login(self):
        #register a new account
        response = self.client.post('/auth/register', data={
            'email': 'john@example.com',
            'username': 'john',
            'password': 'cat',
            'password2': 'cat',
            'about_me' :'Likes to Get Shwifty'
            })
        self.assertEqual(response.status_code, 200)

        #login with new account
        response = self.client.post('/auth/login', data={
            'email': 'john@example.com',
            'password':'cat'
            }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
        #log out
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse('You have been logged out!' in response.get_data(as_text=True))
        













        

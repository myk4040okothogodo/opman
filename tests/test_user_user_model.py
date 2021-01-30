import unittest
from app.models import User
import time
from datetime import datetime
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission,Account,Opportunity


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash  != u2.password_hash)
 
    def test_user_role(self):
        u = User(email='john@example.com', password='cat')
        self.assertTrue(u.can(Permission.CREATE_ACCOUNTS))
        self.assertTrue(u.can(Permission.CREATE_OPPORTUNITY))
        self.assertTrue(u.can(Permission.VIEW_OPPORTUNITIES))
        self.assertFalse(u.can(Permission.DELETE_ACCOUNTS))
        self.assertFalse(u.can(Permission.ADMINISTER))
        

    def test_moderator_role(self):
        r = Role.query.filter_by(name='Moderator').first()
        u = User(email='john@example.com', password='cat', role=r)
        self.assertTrue(u.can(Permission.CREATE_ACCOUNTS))
        self.assertTrue(u.can(Permission.CREATE_OPPORTUNITY))
        self.assertTrue(u.can(Permission.VIEW_OPPORTUNITIES))
        self.assertFalse(u.can(Permission.DELETE_ACCOUNTS))
        self.assertFalse(u.can(Permission.ADMINISTER))   

    def test_administrator_role(self):
        r = Role.query.filter_by(name='Administrator').first()
        u = User(email='john@example.com', password='cat', role=r)
        self.assertTrue(u.can(Permission.CREATE_ACCOUNTS))
        self.assertTrue(u.can(Permission.CREATE_OPPORTUNITY))
        self.assertTrue(u.can(Permission.VIEW_OPPORTUNITIES))
        self.assertTrue(u.can(Permission.DELETE_ACCOUNTS))
        self.assertTrue(u.can(Permission.ADMINISTER))    

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.CREATE_ACCOUNTS))
        self.assertFalse(u.can(Permission.CREATE_OPPORTUNITY))
        self.assertFalse(u.can(Permission.VIEW_OPPORTUNITIES))
        self.assertFalse(u.can(Permission.DELETE_ACCOUNTS))
        self.assertFalse(u.can(Permission.ADMINISTER)) 

    def test_timestamps(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        self.assertTrue(
            (datetime.utcnow() - u.member_since).total_seconds()< 3)
        self.assertTrue(
            (datetime.utcnow() - u.last_seen).total_seconds() < 3)

    def test_ping(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        time.sleep(2)
        last_seen_before = u.last_seen
        u.ping()
        self.assertTrue(u.last_seen > last_seen_before)

    def test_gravatar(self):
        u = User(email='john@example.com', password='cat')
        with self.app.test_request_context('/'):
            gravatar = u.gravatar()
            gravatar_256 = u.gravatar(size=256)
            gravatar_pg = u.gravatar(rating='pg')
            gravatar_retro = u.gravatar(default='retro')
        #self.assertTrue('https://secure.gravatar.com/avatar/' +
                        #'d4c74594d841139328695756648b6bd6'in gravatar)
        self.assertTrue('s=256' in gravatar_256)
        self.assertTrue('r=pg' in gravatar_pg)
        self.assertTrue('d=retro' in gravatar_retro)    
    
        

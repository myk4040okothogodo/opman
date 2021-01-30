from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app,request
from . import db
from datetime import datetime
import hashlib


class Permission:
    CREATE_ACCOUNTS=0x01#(bit value 0b00000001), user is allowed to create account
    CREATE_OPPORTUNITY=0x02#(bit value 0b00000010),user is allowed to add opportunities
    VIEW_OPPORTUNITIES=0x04#(bit value 0b00000100), user is allowed to view opportunities
    DELETE_ACCOUNTS = 0x08
    ADMINISTER=0x80#(bit value 0b10000000)
    
class Role(db.Model):
    __tablename__ ='roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index= True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.CREATE_ACCOUNTS| Permission.CREATE_OPPORTUNITY| Permission.VIEW_OPPORTUNITIES, True ),
            'Moderator':(Permission.CREATE_ACCOUNTS| Permission.CREATE_OPPORTUNITY| Permission.VIEW_OPPORTUNITIES|Permission.DELETE_ACCOUNTS,False ),
            'Administrator':(0xff, False)
            }
        for r in roles:
            role = Role.query.filter_by(name = r).first()
            if role is None:
                role = Role( name = r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]    
            db.session.add(role)    
        db.session.commit()      
    def __repr__(self):
        return '<Role %r>' %self.name

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    about_me = db.Column(db.Text())
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    avatar_hash = db.Column(db.String(32)) 
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    opportunities = db.relationship('Opportunity', backref='author', lazy='dynamic')
    accounts = db.relationship('Account', backref='creator', lazy='dynamic')
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['APPLICATION_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

  
               
    @property
    def password(self):
        raise AttributeError('Attention!!,password is read-prohibited')
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def gravatar(self, size=100, default='identicon', rating='pg'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions)

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)
    
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
    def __repr__(self):
        return '<User %r>' %self.username
    
    

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     about_me =forgery_py.lorem_ipsum.sentence(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()    
    
    """
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    """
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    def is_administrator(self):
        return False
    
login_manager.anonymous_user = AnonymousUser    


class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(64),  index=True)
    company_address = db.Column(db.String(64))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    opportunities = db.relationship('Opportunity', backref='account', lazy='dynamic')
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u=User.query.offset(randint(0, user_count-1)).first()
            a = Account(company_name=forgery_py.name.company_name(),
                        company_address=forgery_py.address.street_address(),
                        creator=u,
                        timestamp =forgery_py.date.date(True))
            db.session.add(a)
            db.session.commit()            
                                                                
class Opportunity(db.Model):
    __tablename__ = 'opportunities'
    id = db.Column(db.Integer, primary_key=True)
    position_name = db.Column(db.String(), index=True)
    no_of_positions = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u=User.query.offset(randint(0, user_count-1)).first()
            o = Account(position_name=forgery_py.name.job_title_suffix(),
                        no_of_position=forgery_py.personal.shirt_size(),
                        timestamp =forgery_py.date.date(True),
                        author=u)
            db.session.add(o)
            db.session.commit()                     
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

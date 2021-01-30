import os
basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'houdini'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    APPLICATION_MAIL_SUBJECT_PREFIX = '[Opportunity management]'
    APPLICATION_ADMIN = 'admin@gmail.com' or 'mikeokoth4040@gmail.com' or 'mikeogodo@gmail.com'
    APP_COMMENTS_PER_PAGE =  15
    SSL_DISABLE = True
    @staticmethod
    def init_app(app):
        pass
class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT =   587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'sqlite:///'+os.path.join(basedir, 'data-dev.sqlite')
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///'+ os.path.join(basedir, 'data-test.sqlite')
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABSE_URL') or \
                              'sqlite:///'+os.path.join(basedir, 'data.sqlite')
class HerokuConfig(ProductionConfig):
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        #handle proxy serever headers
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app) 
        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)
        
config = {
    'development': DevelopmentConfig,
    'testing' :  TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
    'heroku':HerokuConfig
    }
    
    

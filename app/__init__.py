import os
from flask import Flask, Blueprint
from flask_restplus import Api
from flask_cors import CORS
from flask_bcrypt import Bcrypt


from instance.config import app_config
from .api.v1.bucketlist import bucketlist_api
from .api.v1.auth import auth_api
from .api.v1.item import item_api
from .models.baseModel import db

bcrypt = Bcrypt()

# Create v1 blueprint for api
api_v1 = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(api_v1, version='1.0', title='BucketList API',
          description='api to allow the creation & control of bucketlists')

api.add_namespace(bucketlist_api)
api.add_namespace(auth_api)
api.add_namespace(item_api)


def create_app(config_name):

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    CORS(app)

    app.register_blueprint(api_v1)
    db.init_app(app)
    bcrypt.init_app(app)

    return app

my_app = create_app(config_name=os.getenv('APP_SETTINGS') or 'development')

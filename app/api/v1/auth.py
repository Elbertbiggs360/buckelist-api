from flask import request, g
from flask_restplus import abort, Resource, Namespace, fields
from app.models.user import User
from app.utils.utilities import validate_email, auth


auth_api = Namespace(
    'auth', description='User authentication and registration')

user_fields = auth_api.model(
    'User',
    {
        'first_name': fields.String(
            required=True, description='User first name', example='fName'),
        'last_name': fields.String(
            required=True, description='User last name', example='lName'),
        'email': fields.String(
            required=True, description='User email', example='lname@test.com'),
        'password': fields.String(
            required=True, description='User password', example='123'),
    })


@auth_api.route('/register', endpoint='register')
class RegisterUser(Resource):
    ''' Class for User Registration '''
    @auth_api.response(201, 'User registration successfull.')
    @auth_api.response(409, 'User already Exists!. Login')
    @auth_api.response(400, 'Error while creating your account:')
    @auth_api.response(400, 'Password doesn\'nt match confirmation')
    @auth_api.response(500, 'Server Error. Couldn\'t complete request')
    @auth_api.doc(model='User', body=user_fields)
    def post(self):
        ''' Method to handle POST request for User registration '''
        arguments = request.get_json(force=True)
        first_name, last_name, email = arguments.get(
            'first_name').strip(), arguments.get('last_name').strip(), arguments.get('email').lower().strip()
        password, password_confirm = arguments.get(
            'password').strip(), arguments.get('password_confirm').strip()

        if not validate_email(email):
            return abort(400, message='email address is invalid.')
        if not first_name or not last_name:
            return abort(400, 'First Name AND Last Name should be provided')
        if not password or not password_confirm:
            return abort(400, 'Password must be provided')
        if password != password_confirm:
            return abort(401, message='Password doesn\'t match confirmation')

        user = User(email=email, first_name=first_name,
                    last_name=last_name, password=password)

        try:
            confirm = user.save_user()
            if confirm:
                response = {'message': 'User registration successful.'}
                return response, 201
            else:
                response = {'message': 'User already Exists!. Login'}
                return response, 409
        except Exception as e:
            abort(400, 'Error while creating your account: {}'.format(e))


@auth_api.route('/login', endpoint='login')
class AuthenticateUser(Resource):


    @auth_api.response(202, 'Login Successful')
    @auth_api.response(400, 'Bad Request')
    @auth_api.response(401, 'Wrong password')
    @auth_api.response(500, 'Internal Server Error')
    def post(self):
        ''' Method to handle POST request for User LOGIN '''
        arguments = request.get_json(force=True)
        email, password = arguments.get('email').strip(), arguments.get('password').strip()

        if not validate_email(email):
            return abort(400, message='Please provide valid email credentials.')
        if not password:
            return abort(400, message='Password cannot be empty')
        user = User.query.filter_by(email=email).first()
        try:
            if not user:
                return {'message': 'Email not found'}, 400
            if user.verify_password(password):
                token = user.generate_auth_token()
                g.user, g.token = user, token.decode('utf-8')
                if token:
                    result = {'token': g.token}
                    return result, 200
            return {'message': 'Wrong password'}, 401
        except Exception as e:
            return abort(500, 'Error logging in user:{}'.format(e.message))

@auth_api.route('/logout', endpoint='logout')
class Logout(Resource):
    @auth.login_required
    @auth_api.response(500, 'Internal Server Error')    
    def get(self):
        ''' Method to log out user '''
        g.user = None
        return {'message': 'ok'}, 200

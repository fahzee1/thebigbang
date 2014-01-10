from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization, Authorization
from django.contrib.auth.models import User
from models import UserProfile, MINIMUM_PASSWORD_LENGTH, validate_password
from tastypie.authentication import BasicAuthentication, ApiKeyAuthentication, MultiAuthentication, Authentication
from django.contrib.auth import authenticate, login, logout
from tastypie.http import HttpUnauthorized, HttpForbidden , HttpBadRequest
from django.http import HttpResponseBadRequest, HttpResponse
from django.conf.urls import url
from tastypie.utils import trailing_slash
from tastypie import fields
from tastypie.serializers import Serializer
from tastypie.models import ApiKey
from django.db import IntegrityError
from exceptions import CustomBadRequest
from django.contrib.auth.hashers import make_password, check_password, is_password_usable
import pdb

responder = {}
class UserResource(ModelResource):
	"""
	Login:
	POST to /api/v1/user/login
	{"username":"user",
	"password":"pword}

	Logout:
	GET to /api/v1/user/logout
	no params

	Update Settings:
	POST to /api/v1/user/settings
	action params:
		-updateEmail
		-updateUsername
		-updatePhoneNumber

	{"username":"user"
	 "action":"updateEmail,
	 "content":"test@email.com"}

	"""

	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
		excludes = ['is_active','is_staff','is_superuser',
					'first_name','last_name','password']
		allowed_methods = ['get','post']
		authorization = DjangoAuthorization()
		authentication = ApiKeyAuthentication()


	def authorized_read_list(self, object_list, bundle):
		return object_list.filter(id=bundle.request.user.id).select_related()


	def prepend_urls(self):
		return [
				url(r'^(?P<resource_name>%s)/login%s$' %
	                (self._meta.resource_name, trailing_slash()),
	                self.wrap_view('login'), name='api_login'),
	            url(r'^(?P<resource_name>%s)/logout%s$' %
	                (self._meta.resource_name, trailing_slash()),
	                self.wrap_view('logout'), name='api_logout'),
	            url(r'^(?P<resource_name>%s)/settings%s$' %
	                (self._meta.resource_name, trailing_slash()),
	                self.wrap_view('settings'), name='api_settings'),
	            ]

	"""
	def hydrate(self, bundle):
		#pdb.set_trace()
		REQUIRED_USER_FIELDS = ['username', 'password']
		for field in REQUIRED_USER_FIELDS:
			if field not in REQUIRED_USER_FIELDS:
				raise CustomBadRequest(code=-10,
									message='%s is required for user resource',
									my_error=True)
		try:
			username = bundle.data['username']
			password = bundle.data['password']
			user = authenticate(username=username,password=password)
			if user:
				if user.is_active:
					login(bundle.request,user)
				else:
					raise CustomBadRequest(code=-1, 
										message='Inactive user')
			else:
				raise CustomBadRequest(code=-1, 
									message='Incorrect user or password')

		except KeyError:
			pass

		return bundle

	"""
	def login(self, request, **kwargs):
		self.method_check(request, allowed=['post'])
		
		data = self.deserialize(request, request.body , format=request.META.get('CONTENT_TYPE', 'application/json'))
		username = data.get('username', None)
		password = data.get('password', None)


		user = authenticate(username=username, password=password)
		if user:
			if user.is_active:
				login(request, user)
				responder['code'] = 1
				return self.create_response(request, responder)
			else:
				raise CustomBadRequest(code=-1, 
									message='Inactive user')
		else:
			raise CustomBadRequest(code=-1, 
								message='Incorrect user or password')

	def logout(self, request, **kwargs):
		self.method_check(request, allowed=['get'])
		if request.user and request.user.is_authenticated():
			logout(request)
			responder['code'] = 1
			responder['message'] = 'Successfull Logout'
			return self.create_response(request, responder)
		else:
			raise CustomBadRequest(code=-1,
								message='User was never authenticated')

	def settings(self, request, **kwargs):
		self.method_check(request, allowed=['post'])
		data = self.deserialize(request, request.body , format=request.META.get('CONTENT_TYPE', 'application/json'))
		username = data.get('username',None)
		action = data.get('action',None)

		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			raise CustomBadRequest(code=-10,
								 message='User Doesnt exist! Thats your fault CJ!',
								 my_error=True)

		new_content = data.get('content',None)
		if action == 'updateEmail':
			user.email = new_content
			try:
				user.save()
				responder['success'] = 1
				responder['message'] = 'Email updated'
				return self.create_response(request,responder)
			except:
				raise CustomBadRequest(code=-1,
									 message='Failed to update email. Wrong format try again.')

		if action == 'updateUsername':
			user.username = new_content
			try:
				user.save()
				responder['success'] = 1
				responder['message'] = 'Username updated'
				return self.create_response(request, responder)
			except:
				raise CustomBadRequest(code=-1, 
									message='Failed to update username. Type new name and try again')

		if action == 'updatePhoneNumber':
			user.userprofile.phone_number = new_content
			try:
				user.userprofile.save()
				responder['success'] = 1
				responder['message'] = 'Phone number updated'
				return self.create_response(request, responder)
			except:
				raise CustomBadRequest(code=-1, 
									message='Failed to update phone number. Please try again')

	def dehydrate(self,bundle):
		try:
			bundle.data['phone_number'] = bundle.obj.userprofile.phone_number
			bundle.data['score'] = bundle.obj.userprofile.score
			bundle.data['facebook_user'] = bundle.obj.userprofile.facebook_user
			bundle.data['last_activity'] = bundle.obj.userprofile.last_activity
		except KeyError:
			pass

		return bundle


class RegisterUserResource(ModelResource):
	"""
	creates a new user and returns http status 201 (code=1) if 
	successful, status 400 (code=-1) if not, and status 500 (code=-10)
	if error on our end. Check "message" in response to know exact error

	POST to /api/v1/register
	{"username":"user",
	 "email":"email",
	 "password":"password"}

	"""

	class Meta:
		resource_name = 'register'
		allowed_methods = ['post']
		include_resource_uri = False
		always_return_data = True
		authorization = Authorization()
		authentication = Authentication()


	def hydrate(self, bundle):
		"""	
		Receive request data here.
		"""
		REQUIRED_USER_FIELDS = ["username", "email", "password"]
		for field in REQUIRED_USER_FIELDS:
			if field not in bundle.data:
				raise CustomBadRequest(code=-10, 
									message="Must provide %s to register" % field,
									my_error =True)

		return bundle

	def obj_create(self, bundle, request=None, **kwargs):
		try:
			username, email, password = bundle.data['username'], bundle.data['email'], bundle.data['password']
			#first, check if a user uses this email
			if User.objects.filter(email=email):
				raise CustomBadRequest(code=-1, 
									message="That email is already used.")

			#second, check if this username is taken
			if User.objects.filter(username=username):
				raise CustomBadRequest(code=-1, 
									message="That username is already taken")

			#third, check if the password is valid
			if len(password) < MINIMUM_PASSWORD_LENGTH:
				raise CustomBadRequest(code=-1, message="Your password should contain"
												 	" at least %d characters" % MINIMUM_PASSWORD_LENGTH)

			#if passed all checks create user
			bundle.obj = User.objects.create_user(username, email, password)

		except KeyError as missing_key:
			raise CustomBadRequest(code=-10,
								message="Must provide %s when creating User CJ!" % missing_key,
								 my_error=True)

		except IntegrityError:
			raise CustomBadRequest(code=-10, message="Username already exists."
												" Shouldnt be seeing this message though!",
											 my_error=True)

		return bundle


	def dehydrate(self, bundle):
		"""
		Spit back data in response here
		"""

		bundle.data['api_key'] = bundle.obj.api_key.key
		bundle.data['userID'] = bundle.obj.id

		try:
			del bundle.data['password']
			del bundle.data['email']
		except KeyError:
			pass

		return bundle











from django.db import models
from tastypie.models import create_api_key
from models import create_profile

#create api key
models.signals.post_save.connect(create_api_key, sender=User)

#create user profile
models.signals.post_save.connect(create_profile, sender=User)

"""
to send api key:
As a header
Format is ``Authorization: ApiKey <username>:<api_key>
Authorization: ApiKey daniel:204db7bcfafb2deb7506b89eb3b9b715b09905c8

As GET params
http://127.0.0.1:8000/api/v1/entries/?username=test&api_key=0f85a5a5429966ba223170bcaaebc1a60e63a6f0

to re generate key:

api_key = ApiKey.objects.get_or_create(user=someuser)
api_key[0].key = api_key.generate_key()
api_key.save()

"""
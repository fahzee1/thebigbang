from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization, Authorization
from django.contrib.auth.models import User
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
		fields = ['username','email']
		allowed_methods = ['get','post']
		authorization = DjangoAuthorization()
		authentication = ApiKeyAuthentication()


	def prepend_urls(self):
		return [
	            url(r"^(?P<resource_name>%s)/login%s$" %
	                (self._meta.resource_name, trailing_slash()),
	                self.wrap_view('login'), name="api_login"),
	            url(r'^(?P<resource_name>%s)/logout%s$' %
	                (self._meta.resource_name, trailing_slash()),
	                self.wrap_view('logout'), name='api_logout'),
	            url(r'^(?P<resource_name>%s)/signup%s$' %
	                (self._meta.resource_name, trailing_slash()),
	                self.wrap_view('logout'), name='api_logout'),
	            url(r'^(?P<resource_name>%s)/settings%s$' %
	                (self._meta.resource_name, trailing_slash()),
	                self.wrap_view('settings'), name='api_settings'),
	            ]


	def login(self, request, **kwargs):
		self.method_check(request, allowed=['post'])
		
		data = self.deserialize(request, request.body , format=request.META.get('CONTENT_TYPE', 'application/json'))
		username = data.get('username', None)
		password = data.get('password', None)


		user = authenticate(username=username, password=password)
		if user:
			if user.is_active:
				login(request, user)
				api_key = ApiKey.objects.get(user=user)
				responder['success'] = 1
				return self.create_response(request, responder)
			else:
				responder['success'] = 0
				responder['message'] = 'disabled'
				return self.create_response(request, responder, HttpForbidden )
		else:
			responder['success'] = 0
			responder['message'] = 'incorrect'
			return self.create_response(request, responder, HttpUnauthorized )

	def logout(self, request, **kwargs):
		self.method_check(request, allowed=['get'])
		if request.user and request.user.is_authenticated():
			logout(request)
			responder['success'] = 1
			return self.create_response(request, responder)
		else:
			responder['success'] = 0
			return self.create_response(request, responder, HttpUnauthorized)

	def settings(self, request, **kwargs):
		self.method_check(request, allowed=['post'])
		data = self.deserialize(request, request.body , format=request.META.get('CONTENT_TYPE', 'application/json'))
		username = data.get('username',None)
		action = data.get('action',None)

		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			responder['success'] = -10
			responder['message'] = 'User Doesnt exist! Thats your fault CJ!'
			return self.create_response(request,responder)

		new_content = data.get('content',None)
		if action == 'updateEmail':
			user.email = new_content
			try:
				user.save()
				responder['success'] = 1
				responder['message'] = 'Email updated'
				return self.create_response(request,responder)
			except:
				responder['success'] = 0
				responder['message'] = 'Failed to update email. Wrong format try again.'
				return self.create_response(request,responder)

		if action == 'updateUsername':
			user.username = new_content
			try:
				user.save()
				responder['success'] = 1
				responder['message'] = 'Username updated'
				return self.create_response(request, responder)
			except:
				responder['success'] = 0
				responder['message'] = 'Failed to update username. Type new name and try again'
				return self.create_response(request,responder)

		if action == 'updatePhoneNumber':
			user.userprofile.phone_number = new_content
			try:
				user.userprofile.save()
				responder['success'] = 1
				responder['message'] = 'Phone number updated'
				return self.create_response(request, responder)
			except:
				responder['success'] = 0
				responder['message'] = 'Failed to update phone number. Please try again'
				return self.create_response(request, responder)

			






class RegisterUserResource(ModelResource):
	"""
	creates a new user and returns http status 201 (created) if 
	successful, else raises error 'username exists'

	POST to /api/v1/register
	{"username":"user",
	 "email":"email",
	 "password":"password"}

	"""
	class Meta:
		object_class = User
		resource_name = 'register'
		fields = ['username']
		allowed_methods = ['post']
		include_resource_uri = False
		always_return_data = True
		authorization = Authorization()
		authentication = Authentication()


	def obj_create(self, bundle, request=None, **kwargs):
		#pdb.set_trace()
		username, email, password = bundle.data['username'], bundle.data['email'], bundle.data['password']
		try:
			bundle.obj = User.objects.create_user(username, email, password)
			try:
				# get newly created api key and return to client
				# also remove sensitve data 
				api_key = ApiKey.objects.get(user=bundle.obj)
				bundle.data['apikey'] = api_key.key
				bundle.data.pop('username')
				bundle.data.pop('password')
				bundle.data.pop('email')
			except:
				# TODO figure out what i need to do here
				pass
		except IntegrityError:
			responder['success'] = 0
			responder['message'] = 'Username already exists'
			return self.create_response(bundle.request,responder)
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
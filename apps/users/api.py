from tastypie.resources import ModelResource
from models import Entry
from tastypie.authorization import DjangoAuthorization
from django.contrib.auth.models import User
from tastypie.authentication import BasicAuthentication, ApiKeyAuthentication, MultiAuthentication
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


class LoginUserResource(ModelResource):
	"""
	Logs users in, overrides default urls to add
	/login and /logout urls.
	"""
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
		fields = ['username','email']
		allowed_methods = ['get','post']
		authorization = DjangoAuthorization()
		authentication = MultiAuthentication(ApiKeyAuthentication(), BasicAuthentication())


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
	            ]


	def login(self, request, **kwargs):
		self.method_check(request, allowed=['post'])
		
		data = self.deserialize(request, request.body , format=request.META.get('CONTENT_TYPE', 'application/json'))
		username = data.get('username', '')
		password = data.get('password', '')


		user = authenticate(username=username, password=password)
		if user:
			if user.is_active:
				login(request, user)
				api_key = ApiKey.objects.get(user=user)
				return self.create_response(request, {
	                   'success': 1
	                })
			else:
				return self.create_response(request, {
	                   'success': 0,
	                   'reason': 'disabled',
	                    }, HttpForbidden )
		else:
			return self.create_response(request, {
	                'success': 0,
	                'reason': 'incorrect',
	                }, HttpUnauthorized )

	def logout(self, request, **kwargs):
		self.method_check(request, allowed=['get'])
		if request.user and request.user.is_authenticated():
			logout(request)
			return self.create_response(request, { 'success': 1 })
		else:
			return self.create_response(request, { 'success': 0 }, HttpUnauthorized)


class EntryResource(ModelResource):
	user = fields.ForeignKey(LoginUserResource, 'user'
		)
	class Meta:
		queryset = Entry.objects.all()
		allowed_methods = ['get','post']
		resource_name = 'entry'
		#authorization = DjangoAuthorization()




class RegisterUserResource(ModelResource):
	"""
	creates a new user and returns http status 201 (created) if 
	successful, else raises error 'username exists'
	"""
	class Meta:
		object_class = User
		resource_name = 'register'
		fields = ['username']
		allowed_methods = ['post']
		include_resource_uri = False
		always_return_data = True
		authorization = DjangoAuthorization()
		authentication = BasicAuthentication()


	def obj_create(self, bundle, request=None, **kwargs):
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
			raise Exception('Username exists')
		return bundle




from django.db import models
from tastypie.models import create_api_key

models.signals.post_save.connect(create_api_key, sender=User)

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
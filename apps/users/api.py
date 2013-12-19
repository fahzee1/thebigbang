from tastypie.resources import ModelResource
from models import Entry
from tastypie.authorization import DjangoAuthorization
from django.contrib.auth.models import User
from tastypie.authentication import BasicAuthentication, ApiKeyAuthentication
from django.contrib.auth import authenticate, login, logout
from tastypie.http import HttpUnauthorized, HttpForbidden
from django.conf.urls import url
from tastypie.utils import trailing_slash
from tastypie import fields
import pdb


class UserResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
		excludes = ['email', 'password', 'is_active', 'is_staff', 'is_superuser']
		list_allowed_methods = ['get','post']
		authorization = DjangoAuthorization()
		authentication = BasicAuthentication()

		def override_urls(self):
			return [
	            url(r"^(?P<resource_name>%s)/login%s$" %
	                (self._meta.resource_name, trailing_slash()),
	                self.wrap_view('login'), name="api_login"),
	            url(r'^(?P<resource_name>%s)/logout%s$' %
	                (self._meta.resource_name, trailing_slash()),
	                self.wrap_view('logout'), name='api_logout')]

		def login(self, request, **kwargs):
			pdb.set_trace()
			self.method_check(request, allowed=['post'])
			data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
			username = data.get('username', '')
			password = data.get('password', '')
			print username

			user = authenticate(username=username, password=password)
			if user:
				if user.is_active:
					login(request, user)
					return self.create_response(request, {
	                    'success': True
	                })
				else:
					return self.create_response(request, {
	                    'success': False,
	                    'reason': 'disabled',
	                    }, HttpForbidden )
			else:
				return self.create_response(request, {
	                'success': False,
	                'reason': 'incorrect',
	                }, HttpUnauthorized )

		def logout(self, request, **kwargs):
			self.method_check(request, allowed=['get'])
			if request.user and request.user.is_authenticated():
				logout(request)
				return self.create_response(request, { 'success': True })
			else:
				return self.create_response(request, { 'success': False }, HttpUnauthorized)

class EntryResource(ModelResource):
	user = fields.ForeignKey(UserResource, 'user'
		)
	class Meta:
		queryset = Entry.objects.all()
		allowed_methods = ['get','post']
		resource_name = 'entry'
		#authorization = DjangoAuthorization()




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
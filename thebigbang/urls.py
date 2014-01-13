import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()
from tastypie.api import Api
from apps.users.api import UserResource, RegisterUserResource ,UserProfileResource
from apps.challenges.api import ChallengeResource

v1_api = Api(api_name="v1")
v1_api.register(UserResource())
v1_api.register(RegisterUserResource())
v1_api.register(UserProfileResource())
v1_api.register(ChallengeResource())

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'thebigbang.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(v1_api.urls)),

)


if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT}))
import pdb
import base64
import cStringIO
import gzip
import zlib
from django.conf.urls import url
from tastypie.utils import trailing_slash
from tastypie.resources import ModelResource
from django.contrib.auth.models import User
from django.core.files import File
from models import Challenge, ChallengeResults
from apps.users.exceptions import CustomBadRequest
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import BasicAuthentication, ApiKeyAuthentication, MultiAuthentication, Authentication
from tastypie.validation import Validation
from tastypie import fields
from django.core.files.base import ContentFile

responder = {}

class ChallengeValidation(Validation):

    def is_valid(self, bundle, request=None):
        errors = {}
        if not bundle.data:
            errors['error'] = 'Must provide data to create challenge!'
            return errors



        return errors



class ChallengeResource(ModelResource):
    """
    Create challenge:
    POST to /api/v1/challenge

    {
      "username":"user",
      "name":"name of challenge",
      "challenge_id":"id",
      "challenge_media":"file",
      "answer":"answer",
      "hint":"hint"
      "media_type":"0",
      "gzip":"1",
      "challenge_type":"type"
    }

     Send challenge:
     POST to /api/v1/send

    {
      "challenge_id":"id",
      "recipients":["user", "user2", "user3"],
      "username":"user"
    }

    Send challenge results:
    POST to /api/v1/results
    success:
         -yes or no


    {
      "username":"user",
      "challenge_id":"id",
      "success":"yes",
      "score":133

    }

    Will send media data as gzipped base64 data
    store it in a (new in 1.6) binary field.
    Send it back to client as gzipped then decompress
    to show image or video

    or can try this, will return data on backend

    if int(gzip):
        data = zlib.decompress(media, 16+zlib.MAX_WBITS)
    """

    class Meta:
        resource_name = 'challenge'
        allowed_methods = ['post']
        include_resource_uri = False
        always_return_data = False
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        validation = ChallengeValidation()


    def prepend_urls(self):
        return [
                url(r'^(?P<resource_name>%s)/send%s$' %(self._meta.resource_name,
                    trailing_slash()),self.wrap_view('send_challenge'), name='api_send'),
                url(r'^(?P<resource_name>%s)/blob%s$' %(self._meta.resource_name,
                    trailing_slash()),self.wrap_view('get_blob'), name='api_blob'),
                url(r'^(?P<resource_name>%s)/recents%s$' %(self._meta.resource_name,
                    trailing_slash()),self.wrap_view('get_recents'), name='api_recents'),
                url(r'^(?P<resource_name>%s)/results%s$' %(self._meta.resource_name,
                    trailing_slash()),self.wrap_view('send_results'), name='api_results'),
                ]


    def send_results(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        data = self.deserialize(request,
                                request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))
        REQUIRED_USER_FIELDS = ["username", "challenge_id", "success"]
        for field in REQUIRED_USER_FIELDS:
            if field not in data:
                raise CustomBadRequest(code=-10,
                                      message="Must provide %s to send challenge results" % field)

        username = data.get('username')
        challenge_id = data.get('challenge_id')
        success = data.get('success')
        score = data.get('score',None)

        try:
            challenge = Challenge.objects.get(challenge_id=challenge_id)
        except Challenge.DoesNotExist:
            raise CustomBadRequest(code=-10,
                                   message="Challenge doesnt exist!")

        try:
            sender = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CustomBadRequest(code=-10,
                                   message="User doesnt exist!")

        try:
            sender.userprofile.played_challenges += 1
            if score:
                sender.userprofile.score = score
            sender.userprofile.save()
        except:
            raise CustomBadRequest(code=-10,
                                   message="Error incrementing player challenges or incrementing score")

        # did user win or lose challenge?
        success = (True if success == 'yes' else False)

        # create challenge results and return success
        try:
            results = ChallengeResults.objects.create(
                                            player=sender,
                                            challenge=challenge,
                                            success=success)
            responder['code'] = 1
            responder['message'] = 'Successfully sent challenge results'
            return self.create_response(request,responder)
        except:
            raise CustomBadRequest(code=-10,
                                   message="Error creating challenge results!")


    def get_recents(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        data = self.deserialize(request,
                                request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))
        REQUIRED_FIELDS = ['username', 'timestamp']
        for field in REQUIRED_FIELDS:
            if field not in data:
                raise CustomBadRequest(-10,
                                        'Must provide %s when fetching challenges' % field)
        username = data.get('username', None)
        timestamp = data.get('timestamp', None)




    def get_blob(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        data = self.deserialize(request,
                                request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))
        username = data.get('username', None)
        challenge_id = data.get('challenge_id', None)
        if not username:
            raise CustomBadRequest(code=-10,
                                   message='Must provide username when sending challenge!')

        if not challenge_id:
            raise CustomBadRequest(code=-10,
                                   message='Must provide challenge id when sending challenge!')

        try:
            challenge = Challenge.objects.get(challenge_id=challenge_id)
            if challenge.active:
                return self.create_response(request, challenge.spit_json)

            else:
                raise CustomBadRequest(code=-1,
                                       message='Challenge no longer active')
        except Challenge.DoesNotExist:
            raise CustomBadRequest(code=-10,
                                   message="Challenge doest exist!")


    def send_challenge(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        data = self.deserialize(request,
                                request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))
        username = data.get('username', None)
        challenge_id = data.get('challenge_id', None)
        recipients = data.get('recipients', None)
        if not username:
            raise CustomBadRequest(code=-10,
                                   message='Must provide username when sending challenge!')

        if not challenge_id:
            raise CustomBadRequest(code=-10,
                                   message='Must provide challenge id when sending challenge!')

        if not recipients:
            raise CustomBadRequest(code=-10,
                                   message='Must provide recipients when sending challenge!')

        try:
            sender = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CustomBadRequest(code=-10,
                                   message='User Doesnt exist! Thats your fault CJ!')

        try:
            challenge = Challenge.objects.get(challenge_id=challenge_id)
        except Challenge.DoesNotExist:
            raise CustomBadRequest(code=-10,
                                   message='Challenge Doesnt exist! Thats your fault CJ!')

        # create challenge send and add all recievers from recipients list
        try:
            send = ChallengeSend()
            send.sender = sender
            send.challenge = challenge
            send.save()
            for reciever in recipients:
                try:
                    user = User.objects.get(username=reciever)
                    send.recipients.add(user)
                except User.DoesNotExist:
                    raise CustomBadRequest(code=-10,
                                   message='User Doesnt exist! Thats your fault CJ!')
            responder['code'] = 1
            responder['message'] = 'Successfully sent challenge!'
            return self.create_response(request, responder)

        except:
            raise CustomBadRequest(code=-10,
                                   message='Not sure what happened, but thats your fault CJ!')


    def hydrate(self, bundle):
        REQUIRED_CHALLENGE_FIELDS = ["username",
                                     "name",
                                     "challenge_id",
                                     "media_type",
                                     "challenge_type",
                                     "answer",
                                     "hint",
                                     "media",
                                     "gzip"]

        for field in REQUIRED_CHALLENGE_FIELDS:
            if field not in bundle.data:
                raise CustomBadRequest(code=-10,
                                       message="Must provide %s when creating challenge" % field)
        return bundle


    def obj_create(self, bundle, request=None, **kwargs):
        username = bundle.data.get('username', None)
        challenge_type = bundle.data.get('challenge_type', None)
        media_type = bundle.data.get('media_type', None)
        name = bundle.data.get('name', None)
        challenge_id = bundle.data.get('challenge_id', None)
        answer = bundle.data.get('answer', None)
        hint = bundle.data.get('hint', None)
        media = bundle.data.get('media', None)
        gzip = bundle.data.get('gzip', None)

        if not username:
            raise CustomBadRequest(code=-10,
                                   message='Must provide username when creating a challenge!')

        if not challenge_type:
            raise CustomBadRequest(code=-10,
                                   message='Must provide challenge_type when creating a challenge!')

        if not media_type:
            raise CustomBadRequest(code=-10,
                                   message='Must provide media_type value when creating a challenge')

        if not name:
            raise CustomBadRequest(code=-10,
                                   message='Must provide name when creating a challenge')
        if not challenge_id:
            raise CustomBadRequest(code=-10,
                                   message='Must provide challenge_id when creating a challenge')

        if not answer:
            raise CustomBadRequest(code=-10,
                                   message='Must provide answer password when creating a challenge')

        if not media:
            raise CustomBadRequest(code=-10,
                                   message='Must provide media when creating a challenge')

        if not gzip:
            raise CustomBadRequest(code=-10,
                                   message='Must provide gzip value when creating a challenge')


        try:
            creator = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CustomBadRequest(code=-10,
                                   message='User Doesnt exist! Thats your fault CJ!')


        try:
            """
            #todo handle different file types
            image_data = base64.b64decode(media)
            bundle.obj = Challenge.objects.create(
                sender=creator,
                name=name,
                media_type=int(media_type),
                challenge_type=int(challenge_type),
                challenge_id=challenge_id,
                answer=answer,
                hint=hint,
                challenge_media=ContentFile(image_data,challenge_id+'.png')
                )
            """

            bundle.obj = Challenge.objects.create(
                sender=creator,
                name=name,
                media_type=int(media_type),
                challenge_type=int(challenge_type),
                challenge_id=challenge_id,
                answer=answer,
                hint=hint,
                media_data = media
                )



        except:
            raise CustomBadRequest(code=-10,
                                  message='Not sure what happened, but its your fault CJ!')

        return bundle




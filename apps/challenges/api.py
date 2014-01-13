import pdb
import base64
import cStringIO
from tastypie.resources import ModelResource
from django.contrib.auth.models import User
from django.core.files import File
from models import Challenge
from apps.users.exceptions import CustomBadRequest
from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.authentication import BasicAuthentication, ApiKeyAuthentication, MultiAuthentication, Authentication
from tastypie.validation import Validation
from tastypie import fields
from django.core.files.base import ContentFile


class ChallengeValidation(Validation):

    def is_valid(self, bundle, request=None):
        errors = {}
        if not bundle.data:
            errors['error'] = 'Must provide data to create challenge!'
            return errors

        

        return errors



class ChallengeResource(ModelResource):
    """
    Create challenge

    {
      "username":"user",
      "name":"name of challenge",
      "challenge_id":"id",
      "challenge_media":"file",
      "answer":"answer",
      "hint":"hint"
      "media_type":0,
      "challenge_type":"type"
    }
    """
    media = fields.FileField(attribute="challenge_media")

    class Meta:
        resource_name = 'challenge'
        allowed_methods = ['post']
        include_resource_uri = False
        always_return_data = True
        authorization = DjangoAuthorization()
        authentication = ApiKeyAuthentication()
        validation = ChallengeValidation()

    def hydrate(self, bundle):
        REQUIRED_CHALLENGE_FIELDS = ["username",
                                     "name",
                                     "challenge_id",
                                     "media_type",
                                     "challenge_type",
                                     "answer",
                                     "hint",
                                     "media"]

        for field in REQUIRED_CHALLENGE_FIELDS:
            if field not in bundle.data:
                raise CustomBadRequest(code=-10,
                                       message="Must provide %s when creating challenge" % field,
                                       my_error=True)
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

        if not username:
            raise CustomBadRequest(code=-1,
                                   message='Must provide username when creating a challenge!',
                                   my_error=True)

        if not challenge_type:
            raise CustomBadRequest(code=-1,
                                   message='Must provide challenge_type when creating a challenge!',
                                   my_error=True)

        if not media_type:
            raise CustomBadRequest(code=-1,
                                   message='Must provide media_type when creating a challenge',
                                   my_error=True)

        if not name:
            raise CustomBadRequest(code=-1,
                                   message='Must provide name when creating a challenge',
                                   my_error=True)
        if not challenge_id:
            raise CustomBadRequest(code=-1,
                                   message='Must provide challenge_id when creating a challenge',
                                   my_error=True)

        if not answer:
            raise CustomBadRequest(code=-1,
                                   message='Must provide answer password when creating a challenge',
                                   my_error=True)

        if not media:
            raise CustomBadRequest(code=-1,
                                   message='Must provide media when creating a challenge',
                                   my_error=True)


        try:
            creator = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CustomBadRequest(code=-10,
                                   message='User Doesnt exist! Thats your fault CJ!',
                                   my_error=True)

        try:
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

        except:
            raise CustomBadRequest(code=-10,
                                  message='Not sure what happened, but its your fault CJ!',
                                  my_error=True)

        return bundle

        




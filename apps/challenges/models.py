import json
from django.db import models
from tastypie.utils.timezone import now
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
import base64
from django.core import serializers


def get_upload_path(instance , filname):
    path = None
    if instance.media_type == 0:
        path = 'photos/%Y/%m/%d'
    if instance.media_type == 1:
        path = 'videos/%Y/%m/%d'
    return path


class TimeStampedModel(models.Model):
    created_on = models.DateTimeField(default=now,auto_now_add=True)

    class Meta:
        abstract = True



class Challenge(TimeStampedModel):
    """
    TODO django 1.6 has new binary filed to store raw data
    might just use that to store base64 photos and videos
    """
    sender = models.ForeignKey(User, blank=False, null=False)
    name = models.CharField(default='level 1', max_length=255,blank=True, null=True)
    challenge_id = models.CharField(max_length=255, blank=False, null=False, unique=True)
    media_data = models.BinaryField()
    media_type = models.IntegerField(default=0, help_text='Picture or video?')
    challenge_type = models.IntegerField(default=0, help_text='What level challenge?')
    answer = models.CharField(max_length=255, blank=False, null=False)
    hint = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return "Challenge: %d User: %s" % (self.id, self.sender.username)


    def spit_data(self):
        blob = serializers.serialize('json',[self,self.sender])
        blob_json = json.loads(blob)
        challenge_json = blob_json[0]['fields']
        user_json = blob_json[1]['fields']

        try:
            del user_json['is_active']
            del user_json['is_superuser']
            del user_json['is_staff']
            del user_json['groups']
            del user_json['user_permissions']
            del user_json['password']
        except KeyError:
            pass

        challenge_json['sender'] = user_json
        challenge_json['code'] = 1
        challenge_json['message'] = 'Challenge fetch was successful'

        """
        blob = {'media':{
                'media_type':self.media_type,
                'data': base64.b64encode(self.media_data)
        }}
        """

        return challenge_json

    spit_json = property(spit_data)

    def get_points(self):
        if self.challenge_type == 0:
            return 5
        if self.challenge_type == 1:
            return 15
        if self.challenge_type == 2:
            return 25


class ChallengeResults(TimeStampedModel):
    challenge = models.ForeignKey(Challenge, blank=False, null=False, related_name='results')
    player = models.ForeignKey(User, blank=False, null=False)
    success = models.BooleanField(default=False)


    def __unicode__(self):
        return "%s played challenge '%s' by %s" %(self.player.username,
                                                  self.challenge.name,
                                                  self.challenge.sender.username)


class ChallengeSend(TimeStampedModel):
    sender = models.ForeignKey(User, blank=False, null=False, related_name='sent_from')
    recipients = models.ManyToManyField(User, blank=False, null=False)
    challenge = models.ForeignKey(Challenge, blank=False, null=False)
    retry = models.BooleanField(default=False)

    def __unicode__(self):
        return "Sent %s's challenge" % self.sender.username



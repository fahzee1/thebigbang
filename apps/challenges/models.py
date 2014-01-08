from django.db import models
from django.contrib.auth.models import User
from apps.users.models import TimeStampedModel


def get_upload_path(instance , filname):
	path = None
	if instance.media_type == 0:
		path = 'photos/%Y/%m/%d'
	if instance.media_type == 1:
		path = 'videos/%Y/%m/%d'
	return path 

class Challenge(TimeStampedModel):
	sender = models.ForeignKey(User, blank=False, null=False)
	challenge_id = models.CharField(max_length=255, blank=False, null=False)
	challenge_media = models.FileField(upload_to=get_upload_path, blank=False, null=False)
	media_type = models.IntegerField(default=0, help_text='Picture or video?')
	challenge_type = models.IntegerField(default=0, help_text='What level challenge?')
	answer = models.CharField(max_length=255, blank=False, null=False)
	hint = models.CharField(max_length=255, blank=True, null=True)


	def __unicode__(self):
		return "Challenge:%d User:%s" % (self.id, self.sender.username)

	def get_points(self):
		if self.challenge_type == 0:
			return 5
		if self.challenge_type == 1:
			return 15
		if self.challenge_type == 2:
			return 25





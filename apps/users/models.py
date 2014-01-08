from django.db import models
from tastypie.utils.timezone import now
from django.contrib.auth.models import User
# Create your models here.


class TimeStampedModel(models.Model):
	created_on = models.DateTimeField(default=now,auto_now_add=True)

	class Meta:
		abstract = True


class UserProfile(TimeStampedModel):
	user = models.OneToOneField(User)
	score = models.IntegerField(default=0, blank=True, null=True)
	phone_number = models.CharField(max_length=15, blank=True, null=True)
	facebook_user = models.BooleanField(default=False , blank=True)


	def __unicode__(self):
		return self.user.username




def create_profile(sender,**kwargs):
	if kwargs['created']:
		UserProfile.objects.create(user=kwargs['instance'])



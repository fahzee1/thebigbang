import re
from django.db import models
from tastypie.utils.timezone import now
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.


class TimeStampedModel(models.Model):
	created_on = models.DateTimeField(default=now,auto_now_add=True)

	class Meta:
		abstract = True


class UserProfile(TimeStampedModel):
	user = models.OneToOneField(User)
	score = models.IntegerField(default=0, blank=True, null=True)
	phone_number = models.CharField(max_length=255, blank=True, null=True)
	facebook_user = models.BooleanField(default=False , blank=True)
	last_activity = models.DateTimeField(default=now,auto_now_add=True)


	def __unicode__(self):
		return self.user.username




def create_profile(sender,**kwargs):
	if kwargs['created']:
		UserProfile.objects.create(user=kwargs['instance'])


"""
example of updating latest last_activity:
UserProfile.objects.filter(user__id=id).update(last_activity=now)
"""

MINIMUM_PASSWORD_LENGTH = 5
REGEX_VALID_PASSWORD = (
    ## Don't allow any spaces, e.g. '\t', '\n' or whitespace etc.
    r'^(?!.*[\s])'
    ## Check for a digit
    '((?=.*[\d])'
    ## Check for an uppercase letter
    #'(?=.*[A-Z])'
    ## check for special characters. Something which is not word, digit or
    ## space will be treated as special character
    #'(?=.*[^\w\d\s])).'
	')'
    ## Minimum 5 characters
    '{' + str(MINIMUM_PASSWORD_LENGTH) + ',}$')
 
 
def validate_password(password):
	if re.match(REGEX_VALID_PASSWORD, password):
		return True
	return False


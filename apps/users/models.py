import re
import base64
import json
import pdb
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from tastypie.utils.timezone import now
from apps.challenges.models import Challenge, ChallengeResults, TimeStampedModel

# Create your models here.



class Friends(TimeStampedModel):
	user = models.ForeignKey(User, related_name='friend_creator_set')
	friend = models.ForeignKey(User, related_name='friend_set')
	display_name = models.CharField(max_length=255, blank=True, null=True)

	def __unicode__(self):
		return "%s is friends with %s" %(self.friend, self.user)



class UserProfile(TimeStampedModel):
	user = models.OneToOneField(User)
	score = models.IntegerField(default=0, blank=True, null=True)
	phone_number = models.CharField(max_length=255, blank=True, null=True)
	facebook_user = models.BooleanField(default=False , blank=True)
	last_activity = models.DateTimeField(default=now,auto_now_add=True)
	device_token = models.CharField(default="",max_length=255)
	privacy = models.IntegerField(default=0)
	sent_challenges = models.IntegerField(default=0)


	def __unicode__(self):
		return self.user.username

	def return_json(self, login=False):
		"""
		creating json response that mirrors that
		of django tastypie for custom login method
		"""
		profile_data = serializers.serialize('json',[self,self.user])
		p_json = json.loads(profile_data)
		profile_json = p_json[0]['fields']
		user_json = p_json[1]['fields']
		try:
			del user_json['is_active']
			del user_json['is_superuser']
			del user_json['is_staff']
			del user_json['groups']
			del user_json['user_permissions']
			del user_json['password']
		except KeyError:
			pass


		profile_json['user'] = user_json
		profile_json['my_friends'] = self.friends
		profile_json['friend_requests'] = self.friend_requests
		profile_json['my_challenges'] = self.my_challenges
		profile_json['received_challenges'] = self.received_challenges
		profile_json['phone_number'] = base64.b64decode(profile_json['phone_number'])

		if login:
			profile_json['code'] = 11
			profile_json['message'] = 'Login was successful.'

		return profile_json

	def my_friends(self):
		"""
		Returns json of all users friends
		"""
		# or use UserObject.friend_creator_set.filter(user=self)
		my_list = []
		blob = {}
		friends = Friends.objects.filter(user=self.user).select_related()
		for friend in friends:
			blob['username'] = friend.friend.username
			blob['display_name'] = friend.display_name
			blob['friend_created'] = friend.created_on
			blob['friends_score'] = friend.friend.userprofile.score
			blob['friends_last_activity'] = friend.friend.userprofile.last_activity
			my_list.append(blob)

		return json.dumps(my_list, cls=DjangoJSONEncoder)

	friends = property(my_friends)

	def my_requests(self):
		"""
		Returns json of all friends that added
		this user as a friend
		"""
		my_list = []
		blob = {}
		friends = Friends.objects.filter(friend=self.user).select_related()
		for friend in friends:
			blob['username'] = friend.user.username
			blob['display_name'] = friend.display_name
			blob['friend_created'] = friend.created_on
			blob['friends_score'] = friend.user.userprofile.score
			blob['friends_last_activity'] = friend.user.userprofile.last_activity
			my_list.append(blob)

		return json.dumps(my_list, cls=DjangoJSONEncoder)

	friend_requests = property(my_requests)

	def my_challenges(self):
		"""
		Returns json of all challenges
		this user has sent
		"""
		
		my_list = []
		blob = {'results':[]}
		challenges = Challenge.objects.filter(sender=self.user).select_related()
		for challenge in challenges:
			blob['id'] = challenge.challenge_id
			blob['media_type'] = challenge.media_type
			blob['challenge_type'] = challenge.challenge_type
			blob['challenge_created'] = challenge.created_on
			blob['name'] = challenge.name
			for result in challenge.results.all():
				result_blob = {'player': result.player.username,
				               'success': result.success}
				blob['results'].append(result_blob)

			my_list.append(blob)

		return json.dumps(my_list, cls=DjangoJSONEncoder)


	my_challenges = property(my_challenges)


	def received_challenges(self):
		"""
		Returns json of all challenges
		this user has received
		"""
		my_list = []
		challenges = ChallengeResults.objects.filter(player=self.user).select_related()
		for challenge in challenges:
			blob = {
				'challenge':{
				   		'id': challenge.challenge.challenge_id,
				   		'media_type': challenge.challenge.media_type,
				   		'challenge_type': challenge.challenge.challenge_type,
				   		'challenge_created': challenge.challenge.created_on,
				   		'name': challenge.challenge.name,
				   		'result':{
				   				'success': challenge.success,
				   				'sender': challenge.challenge.sender.username}
				   			}
				}
			my_list.append(blob)

		return json.dumps(my_list, cls=DjangoJSONEncoder)


	received_challenges = property(received_challenges)









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






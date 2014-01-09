import json
from tastypie.exceptions import TastypieError
from tastypie.http import HttpBadRequest , HttpApplicationError


class CustomBadRequest(TastypieError):

	def __init__(self, code="", message="", my_error=False):
		self.application_error = my_error
		self._response = { 
				"error":
					{"code": code or "not_provided",
					 "message": message or "No error message was provided"}
					 }

	@property 
	def response(self):
		if self.application_error:
			return HttpApplicationError(json.dumps(self._response), content_type="application/json")
		else:
			return HttpBadRequest(json.dumps(self._response),content_type="application/json")
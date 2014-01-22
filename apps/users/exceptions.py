import json
from tastypie.exceptions import TastypieError
from django.http import HttpResponse


class CustomBadRequest(TastypieError):

    def __init__(self, code="", message=""):
        self._response = { 
                    "code": code or "not_provided",
                    "message": message or "No error message was provided"
                     }

    @property 
    def response(self):
        return HttpResponse(json.dumps(self._response),content_type="application/json")




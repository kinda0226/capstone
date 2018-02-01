#coding: utf-8

from __future__ import unicode_literals
from models import *
import datetime

class SiteUserMiddleware(object):
    def process_request(self, request):
        request.siteUser = None
        if 'user_id' in request.session:
            request.siteUser = SiteUser.objects.filter(id=request.session['user_id']).first()

    def process_template_response(self, request, response):
        response.context_data['siteUser'] = request.siteUser
        return response

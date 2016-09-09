from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.http import HttpResponseForbidden
from hbp_app_python_auth.auth import get_access_token, get_token_type, get_auth_header, HbpAuth
from social.apps.django_app.default.models import UserSocialAuth
from uuid import UUID

from .models import CollaboratoryContext

import bleach
import requests


def __hbp_config(request):
    conf = settings.HBP_CONFIG
    conf['auth']['token'] = __get_client_token(request)
    return conf


def __get_client_token(request):
    try:
        social_auth = request.user.social_auth.get()
        return {
            'access_token': get_access_token(social_auth),
            'token_type': get_token_type(social_auth),
            'expires_in': __get_session_expiry_age(request),
        }
    except UserSocialAuth.DoesNotExist:
        raise exceptions.UserTypeException(request.user)


def __get_session_expiry_age(request):
    return request.session.get_expiry_age()


def __is_collaborator(request):
    '''check access depending on context'''

    svc_url = settings.HBP_COLLAB_SERVICE_URL

    context = request.GET.get('ctx')
    if not context:
        return False
    url = '%s/collab/context/%s/' % (svc_url, context)
    headers = {'Authorization': get_auth_header(request.user.social_auth.get())}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return False
    collab_id = res.json()['collab']['id']
    url = '%s/collab/%s/permissions/' % (svc_url, collab_id)
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return False
    return res.json().get('UPDATE', False)

def __get_user_id(request):
    '''gets 6-digit, unique hbp user id'''

    auth = HbpAuth()
    url = auth.USER_DATA_URL
    headers = {'Authorization': get_auth_header(request.user.social_auth.get())}
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return False
    return res.json()['id']

def __get_s3_creds(tag):
    base = settings.S3_BASE_URL
    headers = {'Accept': "application/json"}
    res = requests.get(base+"/tags/"+tag, headers=headers, verify=False)
    if res.status_code != 200:
        return False
    return res.json()['users-by-tag'][0]


@never_cache
@login_required(login_url='/login/hbp/')
def show(request):
    '''Render the wiki page using the provided context query parameter'''
    # check permissions
    if not __is_collaborator(request):
        return HttpResponseForbidden()

    # build the instance
    context = UUID(request.GET.get('ctx'))
    instance = CollaboratoryContext(ctx=context)

    uid = __get_user_id(request)
    s3_creds = __get_s3_creds(uid)
    if s3_creds == False:
        instance.access_key = "N/A"
        instance.secret_key = "N/A"
        instance.uuid = "N/A"
    else:
        instance.access_key = s3_creds['access_key']
        instance.secret_key = s3_creds['secret_key']
        instance.uuid = s3_creds['uuid']

    return render(request, 'show.html', {
        'context': context,
        'model': instance,
        'config': __hbp_config(request),
    })


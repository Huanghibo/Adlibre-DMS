import mimetypes
import os

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.utils.translation import ugettext_lazy as _
from django.views.generic.simple import direct_to_template
from django.http import Http404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse

from fileshare.forms import UploadForm, SettingForm
from fileshare.models import (Rule, available_validators,
    available_splitters)


def index(request, template_name='fileshare/index.html', extra_context={}):
    form = UploadForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            document = os.path.splitext(form.files['file'].name)[0]
            rule = Rule.objects.match(document)
            if not rule:
                return HttpResponse("No rule found for your uploaded file")
            splitter = rule.get_splitter()
            storage = rule.get_storage()
            storage.store(form.files['file'], splitter)
    extra_context['form'] = form
    return direct_to_template(request,
                              template_name,
                              extra_context=extra_context)


def get_file(request, hashcode, document):
    rule = Rule.objects.match(document)
    if not rule:
        raise Http404
    if not rule.is_hash_active:
        raise Http404
    #todo : check file again hashcode
    splitter = rule.get_splitter()
    storage = rule.get_storage()
    mimetype, content = storage.get(document, splitter)
    response = HttpResponse(content, mimetype=mimetype)
    response["Content-Length"] = len(content)
    return response



def get_file_no_hash(request, document):
    rule = Rule.objects.match(document)
    if not rule:
        raise Http404
    if rule.is_hash_active:
        raise Http404
    splitter = rule.get_splitter()
    storage = rule.get_storage()
    mimetype, content = storage.get(document, splitter)
    response = HttpResponse(content, mimetype=mimetype)
    response["Content-Length"] = len(content)
    return response


@staff_member_required
def setting(request, template_name='fileshare/setting.html',
                   extra_context={}):
    rule_list = Rule.objects.all()
    if request.method == 'POST':
        form = SettingForm(request.POST)
        if form.is_valid():
            rule.save()
    else:
        form = SettingForm()

    extra_context['form'] = form
    extra_context['rule_list'] = rule_list
    return direct_to_template(request, template_name, extra_context=extra_context)


@staff_member_required
def edit_setting(request, rule_id, template_name='fileshare/edit_setting.html',
                   extra_context={}):
    rule = get_object_or_404(Rule, id=rule_id)
    form = SettingForm(request.POST or None, instance=rule)
    if request.method == 'POST':
        if form.is_valid():
            rule.save()
            messages.success(request, 'Rule details updated.')
            return HttpResponseRedirect(reverse('setting'))

    extra_context['form'] = form
    return direct_to_template(request, template_name, extra_context=extra_context)


# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
import json
import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
import requests
from settings import API_SERVER

__author__ = 'tchen'
logger = logging.getLogger(__name__)


class GroupView(TemplateView):
    template_name = 'church/group.html'

    def get_users(self, group):
        return requests.get(API_SERVER + '/directory/groups/%s.json' % group).json()

    def get_pr_list(self, uid):
        return requests.get(API_SERVER + '/gnats/%s.json' % uid).json()

    def get_context_data(self, **kwargs):
        group = self.kwargs['text']

        users = self.get_users(group)

        data = []
        for user in users['members']:
            issues = self.get_pr_list(user['uid'])
            data.append({'user': user, 'issues': issues})

        context = super(GroupView, self).get_context_data(**kwargs)

        context['data'] = data
        context['group'] = group

        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GroupView, self).dispatch(*args, **kwargs)


class GroupProgressView(TemplateView):
    template_name = 'church/progress.html'

    def get_context_data(self, **kwargs):
        group = self.kwargs['text']
        day = self.kwargs['text1']
        data = requests.get(API_SERVER + '/gnats/progresses/%s/%s.json' % (group, day)).json()

        context = super(GroupProgressView, self).get_context_data(**kwargs)

        context['manager'] = group

        if data:
            d = data[0]
            context['day'] = d['day'].split('T')[0]
            context['items'] = d['updates'].values()

        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GroupProgressView, self).dispatch(*args, **kwargs)


class GroupRecentProgressView(TemplateView):
    template_name = 'church/recent_progress.html'

    def get_context_data(self, **kwargs):
        group = self.kwargs['text']
        data = requests.get(API_SERVER + '/gnats/progresses/%s/recent.json' % group).json()

        context = super(GroupRecentProgressView, self).get_context_data(**kwargs)

        items = []
        context['manager'] = group
        for item in data:
            items.append({'day': item['day'].split('T')[0], 'updates': item['updates'].values()})

        context['items'] = items
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(GroupRecentProgressView, self).dispatch(*args, **kwargs)
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import Group, Permission, User

from django.db import models
import jsonfield


class Powtoon(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, default='')
    description = models.CharField(max_length=200, blank=True, default='')
    content_json = jsonfield.JSONField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_with_users = models.ManyToManyField(User, related_name='shared_with_users', blank=True)

    class Meta:
        ordering = ('created',)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from models import Powtoon, Permission

admin.site.register(Powtoon)
admin.site.register(Permission)

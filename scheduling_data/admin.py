from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Semester)
admin.site.register(Laboratory)
admin.site.register(Module)
admin.site.register(Participant)
admin.site.register(Assistant)
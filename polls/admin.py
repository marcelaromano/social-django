from django.contrib import admin

from .models import Question, Choice, Website, Oracion, Palabra

admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Palabra)
admin.site.register(Oracion)
admin.site.register(Website)
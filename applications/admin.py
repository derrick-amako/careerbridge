from django.contrib import admin
from .models import Application, Recommendation, StatusHistory

class ApplicationAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        status_changed = True
        if change:
            status_changed = Application.objects.get(pk=obj.pk).status != obj.status
        super().save_model(request, obj, form, change)
        if status_changed:
            StatusHistory.objects.create(application=obj, status=obj.status)

admin.site.register(Application, ApplicationAdmin)
admin.site.register(Recommendation)
admin.site.register(StatusHistory)

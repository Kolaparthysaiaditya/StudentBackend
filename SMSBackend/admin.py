from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Students

@admin.register(Students)
class StudentsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'Sid', 'role')

    def save_model(self, request, obj, form, change):
        if not change or 'password' in form.changed_data:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

from django.contrib import admin
from django.contrib.auth.hashers import make_password, identify_hasher
from .models import Students, Course, Enrollment


@admin.register(Students)
class StudentsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'Sid', 'role')
    search_fields = ('name', 'email', 'Sid')

    def save_model(self, request, obj, form, change):
        # Ensure password is hashed before saving
        try:
            identify_hasher(obj.password)  # If already hashed, do nothing
        except Exception:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('enrollment_id', 'student', 'course', 'marks', 'created_on')
    search_fields = ('enrollment_id', 'student__name', 'course__name')

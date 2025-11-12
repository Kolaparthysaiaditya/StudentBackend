from rest_framework import serializers
from .models import Students, Course, Enrollment
from django.contrib.auth.hashers import make_password

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Students
        fields = "__all__"
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }

    def create(self, validated_data):
        # Do not hash again; Register view already hashes
        return super().create(validated_data)

    def validate(self, data):
        email = data.get('email')
        phone = data.get('phone_number')
        instance = getattr(self, 'instance', None)

        if email:
            qs = Students.objects.filter(email=email)
            if instance:
                qs = qs.exclude(id=instance.id)
            if qs.exists():
                raise serializers.ValidationError({"email": "Email already registered"})

        if phone:
            qs = Students.objects.filter(phone_number=phone)
            if instance:
                qs = qs.exclude(id=instance.id)
            if qs.exists():
                raise serializers.ValidationError({"phone_number": "Phone already registered"})

        # ✅ Must return data correctly (not 'dta')
        return data

class CourseSerializer(serializers.ModelSerializer):
    enrolled_students = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'courseId',
            'name',
            'description',
            'duration',
            'instructor',
            'level',
            'fee',
            'enrolled_students',
        ]

    def get_enrolled_students(self, obj):
        return obj.enrolled_students.count()

class EnrollmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'enrollment_id',
            'student_id', 'student_name',
            'course_id', 'course_name',
            'marks', 'remark', 'status','created_on'
        ]

from django.db import models
from django.utils import timezone
from datetime import datetime
from django.core.validators import RegexValidator

class Students(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('User', 'User'),
    ]
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]
    name = models.CharField(max_length=555)
    email = models.EmailField(unique=True)
    Sid = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=300)
    DOB = models.DateField(null=True, blank=True)
    Address = models.TextField()
    phone_number = models.CharField(max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits."
            )
        ],
        unique=True)
    profile_pic = models.ImageField(
        upload_to='profile_pics/',  
        null=True,
        blank=True
    )
    gender = models.CharField(
        choices=GENDER_CHOICES,
        default="Male",
    )
    role = models.CharField(
        choices=ROLE_CHOICES,
        default='User',
    )

    def __str__(self):
        return f"{self.name} ({self.role})"


class Course(models.Model):
    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    courseId = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in hours or days")
    instructor = models.CharField(max_length=255)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Beginner')
    fee = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        """Auto-generate courseId like CRS25001, CRS25002..."""
        if not self.courseId:
            year_suffix = datetime.now().strftime("%y")
            last_course = Course.objects.filter(courseId__startswith=f"CRS{year_suffix}").order_by('-courseId').first()
            next_num = (
                int(last_course.courseId[5:]) + 1
                if last_course and last_course.courseId[5:].isdigit()
                else 1
            )
            self.courseId = f"CRS{year_suffix}{next_num:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.level})"


class Enrollment(models.Model):
    enrollment_id = models.CharField(max_length=20, unique=True)
    student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrolled_students')
    marks = models.CharField(max_length=10, blank=True, null=True)
    remark = models.TextField(blank=True, null=True) 
    status = models.CharField(max_length=10, blank=True, null=True)
    created_on = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('student', 'course')

    def save(self, *args, **kwargs):
        if not self.enrollment_id:
            year_suffix = datetime.now().strftime("%y")
            last_enroll = Enrollment.objects.filter(
                enrollment_id__startswith=f"ENR{year_suffix}"
            ).order_by('-enrollment_id').first()
            next_num = int(last_enroll.enrollment_id[5:]) + 1 if last_enroll and last_enroll.enrollment_id[5:].isdigit() else 1
            self.enrollment_id = f"ENR{year_suffix}{next_num:03d}"
        if self.marks:
            try:
                marks_value = float(self.marks)
                self.status = "pass" if marks_value >= 35 else "fail"
            except ValueError:
                self.status = None
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enrollment_id} - {self.student.name} - {self.course.name}"


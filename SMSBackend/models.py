from django.db import models
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

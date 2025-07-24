# appname/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10)
    address = models.TextField()
    college = models.CharField(max_length=150, default="Unknown College")
    branch = models.CharField(max_length=100, default="CSE")
    year = models.CharField(max_length=10, default="1st Year")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    roll_number = models.CharField(max_length=20, default="0000")
    dob = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=100, default="Unknown")
    state = models.CharField(max_length=100, default="Unknown")
    pincode = models.CharField(max_length=10, default="000000")
    email = models.EmailField(default="unknown@example.com")
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)


class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class StaffUpdate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    experience = models.PositiveIntegerField(default=0)
    qualification = models.CharField(max_length=100)
    address = models.TextField()
    linkedin = models.URLField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='staff_profiles/', null=True, blank=True)

    def __str__(self):
        return self.full_name


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    uploaded_file = models.FileField(upload_to='course_files/', null=True, blank=True)
    image= models.ImageField(upload_to='course_images/', null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)  # ✅ Approval field

    def __str__(self):
        return self.title
        
class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} enrolled in {self.course.title}"

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='admin_profiles/', default='default.png')

    def __str__(self):
        return self.user.username
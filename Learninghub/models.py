from django.db import models
from django.conf import settings
from django.urls import reverse

# Sponsor model for course sponsorships
class Sponsor(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='sponsor_logos/')
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    sponsor = models.ForeignKey(Sponsor, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['order']

class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    video_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    class Meta:
        ordering = ['order']

class Progress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_lessons = models.ManyToManyField(Lesson, blank=True)
    completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)  # For quizzes or assessments (0-100)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.phoneNumber} - {self.course.title} - {self.completed}"
    
    class Meta:
        unique_together = ('user', 'course')
        verbose_name_plural = 'Progress'

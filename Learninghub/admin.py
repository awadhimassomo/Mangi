from django.contrib import admin
from .models import Course, Lesson, Progress, Sponsor

@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'contact_email', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    list_editable = ('is_active',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'sponsor', 'order')
    search_fields = ('title', 'description')
    list_editable = ('order',)

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('title', 'content', 'video_url', 'order')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'content')
    list_editable = ('order',)

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'completed', 'score', 'completion_date')
    list_filter = ('completed', 'course')
    search_fields = ('user__username',)
    filter_horizontal = ('completed_lessons',)

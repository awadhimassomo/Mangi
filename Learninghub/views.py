from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, Q
from .models import Course, Lesson, Progress, Sponsor
from django.utils import timezone

@login_required
def dashboard(request):
    # Get user's progress data
    user_progress = Progress.objects.filter(user=request.user)
    
    # Calculate overall progress
    total_courses = Course.objects.count()
    completed_courses = user_progress.filter(completed=True).count()
    
    if total_courses > 0:
        overall_progress = (completed_courses / total_courses) * 100
    else:
        overall_progress = 0
    
    # Find the next course to continue
    in_progress_courses = user_progress.filter(completed=False)
    next_course = None
    next_lesson = None
    
    if in_progress_courses.exists():
        next_course = in_progress_courses.first().course
        
        # Find the next uncompleted lesson
        completed_lessons = in_progress_courses.first().completed_lessons.all()
        next_lesson = Lesson.objects.filter(course=next_course).exclude(id__in=completed_lessons.values_list('id', flat=True)).first()
    else:
        # If no courses in progress, suggest the first uncompleted course
        completed_course_ids = user_progress.filter(completed=True).values_list('course_id', flat=True)
        next_course = Course.objects.exclude(id__in=completed_course_ids).first()
        if next_course:
            next_lesson = Lesson.objects.filter(course=next_course).first()
    
    # Get all active sponsors for the carousel
    active_sponsors = Sponsor.objects.filter(is_active=True)

    context = {
        'user_progress': user_progress,
        'overall_progress': overall_progress,
        'next_course': next_course,
        'next_lesson': next_lesson,
        'completed_courses': completed_courses,
        'sponsors': active_sponsors
    }
    
    return render(request, 'learninghub/dashboard.html', context)

@login_required
def sponsor_detail(request, sponsor_id):
    """View for displaying sponsor details and their sponsored courses"""
    sponsor = get_object_or_404(Sponsor, id=sponsor_id)
    
    # Get courses from this sponsor
    sponsored_courses = Course.objects.filter(sponsor=sponsor).order_by('order')
    
    # Get user progress for these courses
    user_progress = {}
    for course in sponsored_courses:
        progress, created = Progress.objects.get_or_create(user=request.user, course=course)
        user_progress[course.id] = {
            'status': 'Completed' if progress.completed else 'In Progress' if progress.completed_lessons.exists() else 'Not Started',
            'percent': (progress.completed_lessons.count() / course.lessons.count() * 100) if course.lessons.count() > 0 else 0
        }
    
    context = {
        'sponsor': sponsor,
        'courses': sponsored_courses,
        'user_progress': user_progress,
    }
    
    return render(request, 'learninghub/sponsor_detail.html', context)

@login_required
def course_list(request):
    # Get filter parameters
    sponsor_id = request.GET.get('sponsor')
    
    # Base queryset
    courses = Course.objects.all().order_by('order')
    
    # Apply filters
    if sponsor_id:
        try:
            sponsor = Sponsor.objects.get(id=sponsor_id)
            courses = courses.filter(sponsor=sponsor)
        except Sponsor.DoesNotExist:
            pass
    
    # Get all active sponsors for filter dropdown
    active_sponsors = Sponsor.objects.filter(is_active=True)
    
    # Get progress status for each course
    user_progress = {}
    for course in courses:
        progress, created = Progress.objects.get_or_create(user=request.user, course=course)
        user_progress[course.id] = {
            'status': 'Completed' if progress.completed else 'In Progress' if progress.completed_lessons.exists() else 'Not Started',
            'percent': (progress.completed_lessons.count() / course.lessons.count() * 100) if course.lessons.count() > 0 else 0
        }
    
    context = {
        'courses': courses,
        'user_progress': user_progress,
        'sponsors': active_sponsors,
        'current_sponsor_id': sponsor_id,
    }
    
    return render(request, 'learninghub/course_list.html', context)

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = Lesson.objects.filter(course=course).order_by('order')
    
    # Get or create progress record
    progress, created = Progress.objects.get_or_create(user=request.user, course=course)
    
    # Mark completed lessons
    completed_lessons = progress.completed_lessons.all()
    completion_status = {lesson.id: lesson in completed_lessons for lesson in lessons}
    
    context = {
        'course': course,
        'lessons': lessons,
        'completion_status': completion_status,
        'progress': progress,
    }
    
    return render(request, 'learninghub/course_detail.html', context)

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.course
    
    # Get or create progress record
    progress, created = Progress.objects.get_or_create(user=request.user, course=course)
    
    # Check if this lesson is already completed
    is_completed = lesson in progress.completed_lessons.all()
    
    # Handle marking lesson as complete
    if request.method == 'POST' and 'mark_complete' in request.POST:
        progress.completed_lessons.add(lesson)
        
        # Check if all lessons in the course are completed
        if progress.completed_lessons.count() == course.lessons.count():
            progress.completed = True
            progress.completion_date = timezone.now()
        
        progress.save()
        return redirect('learninghub:lesson_detail', lesson_id=lesson_id)
    
    # Get previous and next lessons
    prev_lesson = Lesson.objects.filter(course=course, order__lt=lesson.order).order_by('-order').first()
    next_lesson = Lesson.objects.filter(course=course, order__gt=lesson.order).order_by('order').first()
    
    context = {
        'lesson': lesson,
        'course': course,
        'is_completed': is_completed,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
    }
    
    return render(request, 'learninghub/lesson_detail.html', context)

@login_required
def progress_view(request):
    # Get all completed courses for the user
    completed_progress = Progress.objects.filter(user=request.user, completed=True)
    
    context = {
        'completed_progress': completed_progress,
    }
    
    return render(request, 'learninghub/progress.html', context)

@login_required
def sponsor_list(request):
    """View for displaying all active sponsors"""
    sponsors = Sponsor.objects.filter(is_active=True).order_by('name')
    
    context = {
        'sponsors': sponsors,
    }
    
    return render(request, 'learninghub/sponsor_list.html', context)

@login_required
def resources(request):
    """View for displaying learning resources"""
    context = {
        'page_title': 'Learning Resources'
    }
    
    return render(request, 'learninghub/resources.html', context)

@login_required
def tutorials(request):
    """View for displaying tutorials"""
    context = {
        'page_title': 'Tutorials'
    }
    
    return render(request, 'learninghub/tutorials.html', context)

@login_required
def workshops(request):
    """View for displaying workshops"""
    context = {
        'page_title': 'Workshops'
    }
    
    return render(request, 'learninghub/workshops.html', context)

@login_required
def certifications(request):
    """View for displaying certifications"""
    context = {
        'page_title': 'Certifications'
    }
    
    return render(request, 'learninghub/certifications.html', context)

@login_required
def community(request):
    """View for displaying community content"""
    context = {
        'page_title': 'Community'
    }
    
    return render(request, 'learninghub/community.html', context)

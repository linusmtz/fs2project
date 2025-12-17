from django.contrib import admin
from .models import (
    Course,
    Lesson,
    Enrollment,
    LessonProgress,
    CourseRating,
    Comment
)


# =========================
# Course
# =========================
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "identifier", "instructor", "is_listed", "created_at")
    list_filter = ("is_listed", "created_at")
    search_fields = ("title", "description")


# =========================
# Lesson
# =========================
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "content_type", "order")
    list_filter = ("content_type", "course")
    ordering = ("course", "order")


# =========================
# Enrollment
# =========================
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "enrolled_at")
    list_filter = ("course",)


# =========================
# LessonProgress
# =========================
@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "completed", "completed_at")
    list_filter = ("completed",)


# =========================
# CourseRating
# =========================
@admin.register(CourseRating)
class CourseRatingAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "rating", "created_at")
    list_filter = ("rating",)


# =========================
# Comment
# =========================
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "created_at")
    list_filter = ("course", "created_at")
    search_fields = ("content",)

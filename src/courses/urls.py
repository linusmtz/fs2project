from django.urls import path

from .views import (
    CommentCreateView,
    CourseCreateView,
    CourseDeleteView,
    CourseDetailView,
    CourseListView,
    CourseUpdateView,
    EnrollmentCreateView,
    EnrollmentDeleteView,
    LearnerDashboardView,
    LessonCreateView,
    LessonDeleteView,
    LessonDetailView,
    LessonProgressUpdateView,
    LessonReorderView,
    LessonUpdateView,
)

app_name = "courses"

urlpatterns = [
    path("", CourseListView.as_view(), name="course_list"),
    path("dashboard/", LearnerDashboardView.as_view(), name="dashboard"),
    path("create/", CourseCreateView.as_view(), name="course_create"),
    path(
        "<uuid:identifier>/edit/",
        CourseUpdateView.as_view(),
        name="course_update",
    ),
    path(
        "<uuid:identifier>/delete/",
        CourseDeleteView.as_view(),
        name="course_delete",
    ),
    path(
        "<uuid:identifier>/enroll/",
        EnrollmentCreateView.as_view(),
        name="course_enroll",
    ),
    path(
        "<uuid:identifier>/unenroll/",
        EnrollmentDeleteView.as_view(),
        name="course_unenroll",
    ),
    path(
        "<uuid:identifier>/lessons/create/",
        LessonCreateView.as_view(),
        name="lesson_create",
    ),
    path(
        "<uuid:identifier>/lessons/<int:pk>/",
        LessonDetailView.as_view(),
        name="lesson_detail",
    ),
    path(
        "<uuid:identifier>/lessons/<int:pk>/edit/",
        LessonUpdateView.as_view(),
        name="lesson_update",
    ),
    path(
        "<uuid:identifier>/lessons/<int:pk>/delete/",
        LessonDeleteView.as_view(),
        name="lesson_delete",
    ),
    path(
        "<uuid:identifier>/lessons/<int:pk>/progress/",
        LessonProgressUpdateView.as_view(),
        name="lesson_progress",
    ),
    path(
        "<uuid:identifier>/lessons/reorder/",
        LessonReorderView.as_view(),
        name="lesson_reorder",
    ),
    path(
        "<uuid:identifier>/comment/",
        CommentCreateView.as_view(),
        name="comment_create",
    ),
    path("<uuid:identifier>/", CourseDetailView.as_view(), name="course_detail"),
]

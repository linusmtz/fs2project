from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import LessonForm
from .models import Course, Enrollment, Lesson, LessonProgress


User = get_user_model()


class CoursePlatformTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            username="teacher",
            password="pass1234",
            is_staff=True,
        )
        self.student = User.objects.create_user(
            username="student",
            password="pass1234",
        )
        self.course = Course.objects.create(
            instructor=self.instructor,
            title="Python Básico",
            description="Intro a Python.",
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            title="Bienvenida",
            content_type="text",
            text_content="Hola!",
            order=1,
        )

    def test_course_list_search_filters_results(self):
        response = self.client.get(
            reverse("courses:course_list"),
            {"q": "Python"},
        )
        self.assertContains(response, "Python Básico")

        response = self.client.get(
            reverse("courses:course_list"),
            {"q": "No existe"},
        )
        self.assertNotContains(response, "Python Básico")

    def test_course_detail_marks_enrollment_in_context(self):
        Enrollment.objects.create(user=self.student, course=self.course)
        self.client.login(username="student", password="pass1234")
        response = self.client.get(
            reverse("courses:course_detail", args=[self.course.identifier])
        )
        self.assertTrue(response.context["is_enrolled"])

    def test_enrollment_create_view_adds_inscription(self):
        self.client.login(username="student", password="pass1234")
        response = self.client.post(
            reverse("courses:course_enroll", args=[self.course.identifier])
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Enrollment.objects.filter(user=self.student, course=self.course).exists()
        )

    def test_instructor_cannot_enroll_in_own_course(self):
        self.client.login(username="teacher", password="pass1234")
        self.client.post(
            reverse("courses:course_enroll", args=[self.course.identifier])
        )
        self.assertFalse(
            Enrollment.objects.filter(user=self.instructor, course=self.course).exists()
        )

    def test_enrollment_delete_view_removes_inscription(self):
        Enrollment.objects.create(user=self.student, course=self.course)
        self.client.login(username="student", password="pass1234")
        self.client.post(
            reverse("courses:course_unenroll", args=[self.course.identifier])
        )
        self.assertFalse(
            Enrollment.objects.filter(user=self.student, course=self.course).exists()
        )

    def test_lesson_progress_update_marks_completed(self):
        Enrollment.objects.create(user=self.student, course=self.course)
        self.client.login(username="student", password="pass1234")
        self.client.post(
            reverse("courses:lesson_progress", args=[self.course.identifier, self.lesson.id]),
            {"action": "complete"},
        )
        progress = LessonProgress.objects.get(user=self.student, lesson=self.lesson)
        self.assertTrue(progress.completed)

    def test_lesson_creation_requires_instructor(self):
        self.client.login(username="student", password="pass1234")
        response = self.client.get(
            reverse("courses:lesson_create", args=[self.course.identifier])
        )
        self.assertEqual(response.status_code, 403)

    def test_lesson_detail_requires_enrollment(self):
        self.client.login(username="student", password="pass1234")
        response = self.client.get(
            reverse("courses:lesson_detail", args=[self.course.identifier, self.lesson.id])
        )
        self.assertEqual(response.status_code, 403)

    def test_comment_requires_enrollment(self):
        self.client.login(username="student", password="pass1234")
        response = self.client.post(
            reverse("courses:comment_create", args=[self.course.identifier]),
            {"content": "Hola"},
        )
        self.assertEqual(response.status_code, 403)

    def test_lesson_form_validates_content_requirements(self):
        form = LessonForm(
            data={
                "title": "Contenido",
                "content_type": "text",
                "text_content": "",
                "order": 2,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("text_content", form.errors)

    def test_lesson_form_accepts_valid_text_content(self):
        """Test que el formulario acepta lecciones de texto con contenido válido."""
        form = LessonForm(
            data={
                "title": "Lección de texto",
                "content_type": "text",
                "text_content": "Este es el contenido de la lección",
                # order no es requerido, se calcula automáticamente
            }
        )
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_lesson_form_works_without_order(self):
        """Test que el formulario funciona sin el campo order (se calcula automáticamente)."""
        form = LessonForm(
            data={
                "title": "Lección sin order",
                "content_type": "text",
                "text_content": "Contenido de prueba",
                # No incluimos order
            }
        )
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_lesson_create_view_creates_lesson_successfully(self):
        """Test que un instructor puede crear una lección exitosamente."""
        self.client.login(username="teacher", password="pass1234")
        response = self.client.post(
            reverse("courses:lesson_create", args=[self.course.identifier]),
            {
                "title": "Nueva lección",
                "content_type": "text",
                "text_content": "Contenido de la nueva lección",
                # order se calcula automáticamente
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect después de crear
        # Verificar que la lección se creó
        self.assertTrue(
            Lesson.objects.filter(
                course=self.course,
                title="Nueva lección"
            ).exists()
        )
        # Verificar que el order se calculó automáticamente
        new_lesson = Lesson.objects.get(course=self.course, title="Nueva lección")
        self.assertEqual(new_lesson.order, 2)  # Debería ser 2 (después de la lección con order=1)

    def test_lesson_form_validates_video_requires_url_or_attachment(self):
        """Test que las lecciones de video requieren URL o archivo."""
        form = LessonForm(
            data={
                "title": "Video sin contenido",
                "content_type": "video",
                "video_url": "",
                # Sin attachment
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("video_url", form.errors)

    def test_lesson_form_accepts_video_with_url(self):
        """Test que el formulario acepta videos con URL."""
        form = LessonForm(
            data={
                "title": "Video de YouTube",
                "content_type": "video",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            }
        )
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_dashboard_shows_progress_percentage(self):
        Enrollment.objects.create(user=self.student, course=self.course)
        Lesson.objects.create(
            course=self.course,
            title="Segunda",
            content_type="text",
            text_content="Contenido",
            order=2,
        )
        LessonProgress.objects.create(
            user=self.student,
            lesson=self.lesson,
            completed=True,
        )
        self.client.login(username="student", password="pass1234")
        response = self.client.get(reverse("courses:dashboard"))
        self.assertEqual(response.status_code, 200)
        dashboard_courses = response.context["dashboard_courses"]
        self.assertEqual(dashboard_courses[0]["progress_percent"], 50.0)

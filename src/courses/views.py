from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
import json

from .forms import CommentForm, CourseForm, LessonForm, SignupForm, UserProfileForm
from .models import Course, Enrollment, Lesson, LessonProgress


class StaffRequiredMixin(UserPassesTestMixin):
    """Limit the view to staff members only."""

    def test_func(self):
        return self.request.user.is_staff


class CourseInstructorMixin(UserPassesTestMixin):
    """Allow staff or the course instructor to access the view."""

    def get_course(self):
        if hasattr(self, "course"):
            return self.course
        identifier = self.kwargs.get("identifier")
        if identifier:
            self.course = get_object_or_404(Course, identifier=identifier)
            return self.course
        obj = getattr(self, "object", None)
        if obj is None and hasattr(self, "get_object"):
            obj = self.get_object()
        if isinstance(obj, Course):
            self.course = obj
            return self.course
        if hasattr(obj, "course"):
            self.course = obj.course
            return self.course
        raise Http404("Course not found.")

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        course = self.get_course()
        return course.instructor_id == user.id


class CourseListView(ListView):
    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"
    paginate_by = 6

    def get_queryset(self):
        search = self.request.GET.get("q", "")
        instructor_filter = self.request.GET.get("instructor", "")
        
        queryset = (
            Course.objects.filter(is_listed=True)
            .select_related("instructor")
            .prefetch_related("lessons", "enrollments")
            .annotate(
                lesson_count=Count("lessons", distinct=True),
                enrollment_count=Count("enrollments", distinct=True),
            )
            .order_by("-created_at")
        )
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(instructor__first_name__icontains=search) |
                Q(instructor__last_name__icontains=search) |
                Q(instructor__username__icontains=search)
            )
        
        if instructor_filter:
            queryset = queryset.filter(
                Q(instructor__first_name__icontains=instructor_filter) |
                Q(instructor__last_name__icontains=instructor_filter) |
                Q(instructor__username__icontains=instructor_filter)
            )
        
        self.search = search
        self.instructor_filter = instructor_filter
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search"] = getattr(self, "search", "")
        context["instructor_filter"] = getattr(self, "instructor_filter", "")
        
        if self.request.user.is_authenticated:
            context["enrolled_ids"] = set(
                self.request.user.enrollments.values_list("course__identifier", flat=True)
            )
        else:
            context["enrolled_ids"] = set()
        
        # Estadísticas adicionales
        context["total_courses"] = Course.objects.filter(is_listed=True).count()
        context["total_instructors"] = Course.objects.filter(is_listed=True).values("instructor").distinct().count()
        
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"
    slug_field = "identifier"
    slug_url_kwarg = "identifier"

    def get_queryset(self):
        return (
            Course.objects.select_related("instructor")
            .prefetch_related("lessons", "comments__user")
            .annotate(enrollment_count=Count("enrollments", distinct=True))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user

        lessons = list(course.lessons.all())
        context["lessons"] = lessons
        context["comment_form"] = CommentForm()

        is_enrolled = False
        lesson_progress_map = {}

        if user.is_authenticated:
            is_enrolled = Enrollment.objects.filter(
                user=user, course=course
            ).exists()
            progress_qs = LessonProgress.objects.filter(
                user=user, lesson__course=course
            ).select_related("lesson")
            lesson_progress_map = {
                progress.lesson_id: progress for progress in progress_qs
            }

        is_instructor = user.is_authenticated and course.instructor_id == user.id
        context["is_enrolled"] = is_enrolled
        lessons_with_progress = [
            {"lesson": lesson, "progress": lesson_progress_map.get(lesson.id)}
            for lesson in lessons
        ]
        context["lessons_with_progress"] = lessons_with_progress
        context["lesson_progress_map"] = lesson_progress_map
        context["is_instructor"] = is_instructor
        context["can_manage_course"] = user.is_authenticated and (
            user.is_staff or is_instructor
        )

        total_lessons = len(lessons)
        completed = len(
            [lp for lp in lesson_progress_map.values() if lp.completed]
        )
        context["progress_percent"] = (
            round((completed / total_lessons) * 100, 2) if total_lessons else 0
        )

        return context


class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        messages.success(
            self.request, 
            f"¡Curso '{form.instance.title}' creado exitosamente! Ahora puedes agregar lecciones."
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        # Redirigir al curso recién creado
        return self.object.get_absolute_url()


class CourseUpdateView(LoginRequiredMixin, CourseInstructorMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"
    slug_field = "identifier"
    slug_url_kwarg = "identifier"

    def form_valid(self, form):
        messages.success(self.request, "Curso actualizado.")
        return super().form_valid(form)


class CourseDeleteView(LoginRequiredMixin, CourseInstructorMixin, DeleteView):
    model = Course
    template_name = "courses/course_confirm_delete.html"
    slug_field = "identifier"
    slug_url_kwarg = "identifier"
    success_url = reverse_lazy("courses:course_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Curso eliminado.")
        return super().delete(request, *args, **kwargs)


class LessonCreateView(LoginRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = "courses/lesson_form.html"

    def dispatch(self, request, *args, **kwargs):
        identifier = kwargs.get("identifier")
        self.course = get_object_or_404(Course, identifier=identifier)
        
        # Verificar permisos: debe ser el instructor o staff
        if not request.user.is_authenticated:
            return redirect("login")
        if self.course.instructor_id != request.user.id and not request.user.is_staff:
            return HttpResponseForbidden("Solo el instructor del curso puede agregar lecciones.")
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.course = self.course
        # Calcular el order automáticamente: siguiente número después de la última lección
        # Siempre calcular el order, incluso si viene un valor (para evitar conflictos)
        last_lesson = Lesson.objects.filter(course=self.course).order_by('-order').first()
        form.instance.order = (last_lesson.order + 1) if last_lesson else 1
        messages.success(self.request, f"Lección '{form.instance.title}' creada exitosamente.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["course"] = self.course
        return context

    def get_success_url(self):
        return self.course.get_absolute_url()


class LessonUpdateView(LoginRequiredMixin, CourseInstructorMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = "courses/lesson_form.html"

    def get_queryset(self):
        return Lesson.objects.filter(course__identifier=self.kwargs["identifier"])

    def form_valid(self, form):
        instance = form.instance
        
        # Obtener la instancia antigua antes de guardar
        if instance.pk:
            try:
                old_instance = Lesson.objects.get(pk=instance.pk)
                old_attachment = old_instance.attachment
                old_attachment_name = old_attachment.name if old_attachment else None
                old_content_type = old_instance.content_type
            except Lesson.DoesNotExist:
                old_instance = None
                old_attachment = None
                old_attachment_name = None
                old_content_type = None
        else:
            old_instance = None
            old_attachment = None
            old_attachment_name = None
            old_content_type = None
        
        # Guardar primero para que Django maneje el nuevo archivo
        response = super().form_valid(form)
        
        # Después de guardar, verificar si necesitamos eliminar el archivo antiguo
        # IMPORTANTE: Solo eliminar cuando se sube un nuevo archivo (reemplazo explícito)
        # NO eliminar cuando solo se cambia el tipo de contenido, para permitir volver atrás
        if old_attachment and old_attachment_name:
            new_attachment = instance.attachment
            new_attachment_name = new_attachment.name if new_attachment else None
            
            # Solo eliminar el archivo antiguo si se subió un nuevo archivo diferente
            # Esto permite que el usuario cambie el tipo de contenido sin perder el archivo
            should_delete = False
            
            if new_attachment_name and new_attachment_name != old_attachment_name:
                # Se subió un nuevo archivo diferente, eliminar el antiguo
                should_delete = True
            
            if should_delete:
                try:
                    # Verificar que el archivo antiguo aún existe antes de eliminarlo
                    if old_attachment_name and old_attachment.storage.exists(old_attachment_name):
                        # Eliminar el archivo del storage (bucket o local)
                        old_attachment.delete(save=False)
                except Exception as e:
                    # Si falla la eliminación, registrar pero no bloquear
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Error al eliminar archivo antiguo de OCI: {e}")
        
        messages.success(self.request, "Lección actualizada.")
        return response

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class LessonDeleteView(LoginRequiredMixin, CourseInstructorMixin, DeleteView):
    model = Lesson
    template_name = "courses/lesson_confirm_delete.html"

    def get_queryset(self):
        return Lesson.objects.filter(course__identifier=self.kwargs["identifier"])

    def delete(self, request, *args, **kwargs):
        lesson = self.get_object()
        
        # Eliminar el archivo del storage antes de eliminar la lección
        if lesson.attachment:
            try:
                lesson.attachment.delete(save=False)
            except Exception as e:
                # Si falla la eliminación, registrar pero continuar con la eliminación
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error al eliminar archivo de la lección: {e}")
        
        messages.success(request, "Lección eliminada.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = "courses/lesson_detail.html"
    context_object_name = "lesson"

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(
            Course.objects.select_related("instructor"),
            identifier=kwargs["identifier"]
        )
        if not self._has_access(request.user):
            return HttpResponseForbidden("You must enroll in the course to view lessons.")
        return super().dispatch(request, *args, **kwargs)

    def _has_access(self, user):
        if not user.is_authenticated:
            return False
        if user.is_staff or self.course.instructor_id == user.id:
            return True
        return Enrollment.objects.filter(user=user, course=self.course).exists()

    def get_queryset(self):
        return Lesson.objects.filter(course=self.course).select_related("course", "course__instructor")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        progress, _ = LessonProgress.objects.get_or_create(
            user=self.request.user,
            lesson=self.object,
        )
        context["course"] = self.course
        
        # Obtener lecciones anteriores y siguientes para navegación
        all_lessons = list(
            Lesson.objects.filter(course=self.course)
            .order_by("order", "id")
            .values_list("id", flat=True)
        )
        
        context["previous_lesson"] = None
        context["next_lesson"] = None
        
        try:
            current_index = all_lessons.index(self.object.id)
            
            if current_index > 0:
                previous_id = all_lessons[current_index - 1]
                try:
                    context["previous_lesson"] = Lesson.objects.get(id=previous_id)
                except Lesson.DoesNotExist:
                    pass
            
            if current_index < len(all_lessons) - 1:
                next_id = all_lessons[current_index + 1]
                try:
                    context["next_lesson"] = Lesson.objects.get(id=next_id)
                except Lesson.DoesNotExist:
                    pass
        except ValueError:
            # La lección no está en la lista (no debería pasar, pero por seguridad)
            pass
        
        context["progress"] = progress
        return context


class EnrollmentCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        course = get_object_or_404(
            Course.objects.select_related("instructor"),
            identifier=kwargs["identifier"]
        )
        
        if course.instructor_id == request.user.id:
            messages.warning(request, "No puedes inscribirte en un curso que dictas.")
            return redirect(course.get_absolute_url())
        
        if not course.is_listed:
            messages.warning(request, "Este curso no acepta nuevas inscripciones.")
            return redirect(course.get_absolute_url())
        
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user, course=course
        )
        
        if created:
            messages.success(request, f"¡Te inscribiste exitosamente en '{course.title}'!")
            # Log de inscripción
            import logging
            logger = logging.getLogger('courses')
            logger.info(f"User {request.user.username} enrolled in course {course.title}")
        else:
            messages.info(request, "Ya estabas inscrito en este curso.")
        
        return redirect(course.get_absolute_url())


class EnrollmentDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, identifier=kwargs["identifier"])
        deleted, _ = Enrollment.objects.filter(
            user=request.user, course=course
        ).delete()
        if deleted:
            messages.info(request, "Se eliminó tu inscripción.")
        else:
            messages.warning(request, "No estabas inscrito en este curso.")
        return redirect("courses:course_list")


class LessonProgressUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        course = get_object_or_404(
            Course.objects.select_related("instructor"),
            identifier=kwargs["identifier"]
        )
        lesson = get_object_or_404(
            Lesson.objects.select_related("course"),
            pk=kwargs["pk"],
            course=course
        )
        user = request.user

        if not (
            user.is_staff
            or course.instructor_id == user.id
            or Enrollment.objects.filter(user=user, course=course).exists()
        ):
            return HttpResponseForbidden("You must enroll before updating progress.")

        progress, created = LessonProgress.objects.get_or_create(user=user, lesson=lesson)
        action = request.POST.get("action", "toggle")
        position = request.POST.get("position", None)

        if action == "complete":
            was_completed = progress.completed
            progress.mark_completed()
            if not was_completed:
                messages.success(request, f"✅ Lección '{lesson.title}' marcada como completada.")
                # Log de progreso
                import logging
                logger = logging.getLogger('courses')
                logger.info(f"User {user.username} completed lesson {lesson.title} in course {course.title}")
        elif action == "uncomplete":
            progress.completed = False
            progress.completed_at = None
            progress.save(update_fields=["completed", "completed_at"])
            messages.info(request, "La lección quedó pendiente.")
        elif action == "update_position" and position:
            # Para videos, guardar la posición de reproducción
            try:
                position_seconds = int(float(position))
                progress.last_position_seconds = position_seconds
                progress.save(update_fields=["last_position_seconds"])
            except (ValueError, TypeError):
                pass

        # Redirigir según el origen
        redirect_url = request.POST.get("next", course.get_absolute_url())
        return redirect(redirect_url)


class LearnerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "courses/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        enrolled_courses = (
            Course.objects.filter(enrollments__user=user)
            .select_related("instructor")
            .prefetch_related("lessons")
            .distinct()
        )

        progress_entries = LessonProgress.objects.filter(
            user=user, lesson__course__in=enrolled_courses
        ).select_related("lesson", "lesson__course")

        progress_map = {}
        for entry in progress_entries:
            course_id = entry.lesson.course_id
            progress_map.setdefault(course_id, {})[entry.lesson_id] = entry

        dashboard_courses = []
        for course in enrolled_courses:
            lessons = list(course.lessons.all())
            total = len(lessons)
            completed = 0
            lesson_progress = progress_map.get(course.id, {})
            for lesson in lessons:
                progress = lesson_progress.get(lesson.id)
                if progress and progress.completed:
                    completed += 1
            percent = round((completed / total) * 100, 2) if total else 0
            dashboard_courses.append(
                {
                    "course": course,
                    "completed_lessons": completed,
                    "total_lessons": total,
                    "progress_percent": percent,
                }
            )

        context["dashboard_courses"] = dashboard_courses
        context["teaching_courses"] = Course.objects.filter(instructor=user)
        context["total_completed_lessons"] = sum(item["completed_lessons"] for item in dashboard_courses)
        context["total_lessons_available"] = sum(item["total_lessons"] for item in dashboard_courses)
        return context


class LessonReorderView(LoginRequiredMixin, View):
    """Vista AJAX para reordenar lecciones con drag-and-drop"""
    
    def post(self, request, *args, **kwargs):
        course = get_object_or_404(Course, identifier=kwargs["identifier"])
        
        # Verificar permisos
        if not (request.user.is_staff or course.instructor_id == request.user.id):
            return JsonResponse({"error": "No tienes permisos para reordenar lecciones"}, status=403)
        
        try:
            from django.db import transaction
            
            data = json.loads(request.body)
            lesson_orders = data.get("lesson_orders", [])  # Lista de [lesson_id, new_order]
            
            if not lesson_orders:
                return JsonResponse({"error": "No se proporcionaron lecciones para reordenar"}, status=400)
            
            # Validar que todas las lecciones pertenecen al curso
            lesson_ids = [item.get("id") for item in lesson_orders if item.get("id")]
            lessons = Lesson.objects.filter(id__in=lesson_ids, course=course)
            
            if lessons.count() != len(lesson_ids):
                return JsonResponse({"error": "Algunas lecciones no pertenecen a este curso"}, status=400)
            
            # Usar transacción para evitar conflictos de orden único
            with transaction.atomic():
                # Paso 1: Mover todas las lecciones a valores temporales altos para evitar conflictos
                # Usamos valores muy altos (10000+) que no deberían estar en uso normalmente
                temp_offset = 10000
                for lesson in lessons:
                    lesson.order = temp_offset + lesson.id
                    lesson.save(update_fields=["order"])
                
                # Refrescar los objetos desde la base de datos para asegurar que tenemos los valores actualizados
                lessons = Lesson.objects.filter(id__in=lesson_ids, course=course)
                lesson_dict = {lesson.id: lesson for lesson in lessons}
                
                # Paso 2: Actualizar a los valores finales
                for item in lesson_orders:
                    lesson_id = item.get("id")
                    new_order = item.get("order")
                    
                    if lesson_id and new_order is not None and new_order > 0:
                        lesson = lesson_dict.get(lesson_id)
                        if lesson:
                            lesson.order = new_order
                            lesson.save(update_fields=["order"])
            
            return JsonResponse({"success": True, "message": "Lecciones reordenadas exitosamente"})
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Datos inválidos"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class CommentCreateView(LoginRequiredMixin, CreateView):
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, identifier=kwargs["identifier"])
        is_enrolled = Enrollment.objects.filter(
            user=request.user, course=self.course
        ).exists()
        if not (
            is_enrolled
            or request.user.is_staff
            or self.course.instructor_id == request.user.id
        ):
            return HttpResponseForbidden("You must be enrolled to comment.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.course = self.course
        messages.success(self.request, "Comentario publicado.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.course.get_absolute_url()


class SignUpView(CreateView):
    form_class = SignupForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        messages.success(self.request, "Cuenta creada con éxito. Ahora puedes iniciar sesión.")
        return super().form_valid(form)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserProfileForm
    template_name = "registration/profile.html"
    success_url = reverse_lazy("courses:dashboard")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Perfil actualizado.")
        return super().form_valid(form)

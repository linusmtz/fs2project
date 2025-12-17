import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.storage import default_storage
from django.conf import settings

# Helper para obtener el storage correcto
def get_file_storage():
    """Retorna el storage configurado en settings o el default"""
    if hasattr(settings, 'DEFAULT_FILE_STORAGE') and settings.DEFAULT_FILE_STORAGE:
        from django.utils.module_loading import import_string
        storage_class = import_string(settings.DEFAULT_FILE_STORAGE)
        return storage_class()
    return default_storage


# =========================
# Course
# =========================
class Course(models.Model):
    identifier = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )

    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="courses_taught"
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    # Controla si acepta NUEVAS inscripciones
    # NO revoca acceso a usuarios ya inscritos
    is_listed = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("courses:course_detail", kwargs={"identifier": self.identifier})
    
    def get_total_lessons(self):
        """Retorna el número total de lecciones del curso."""
        return self.lessons.count()
    
    def get_total_enrollments(self):
        """Retorna el número total de inscripciones."""
        return self.enrollments.count()
    
    def get_average_rating(self):
        """Retorna el promedio de calificaciones (1-5 estrellas)."""
        from django.db.models import Avg
        avg = self.courserating_set.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else None
    
    def get_total_comments(self):
        """Retorna el número total de comentarios."""
        return self.comments.count()


# =========================
# Lesson
# =========================
class Lesson(models.Model):
    CONTENT_TYPES = [
        ("video", "Video"),
        ("text", "Text"),
        ("image", "Image"),
        ("file", "File"),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons"
    )

    title = models.CharField(max_length=200)

    # Define el tipo de contenido para controlar el progreso
    content_type = models.CharField(
        max_length=10,
        choices=CONTENT_TYPES
    )

    # Contenido opcional dependiendo del tipo
    text_content = models.TextField(blank=True)
    video_url = models.URLField(
        blank=True,
        help_text="URL de video (YouTube, Vimeo, etc.) o deja vacío si subes un archivo de video"
    )

    attachment = models.FileField(
        upload_to="lessons/%Y/%m/%d/",
        blank=True,
        null=True,
        storage=get_file_storage(),  # Usa el storage configurado en settings
        help_text="Sube videos (MP4, WebM, MOV), imágenes (JPG, PNG, GIF) o documentos (PDF, DOC, ZIP)"
    )

    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def get_video_embed_url(self):
        """Convierte URLs de YouTube a formato embed."""
        if not self.video_url:
            return ""
        import re
        # YouTube watch URL: https://www.youtube.com/watch?v=VIDEO_ID
        match = re.search(r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)', self.video_url)
        if match:
            return f"https://www.youtube.com/embed/{match.group(1)}"
        # Si ya es una URL de embed o otra plataforma, devolverla tal cual
        return self.video_url

    def get_file_name(self):
        """Obtiene el nombre del archivo sin la ruta."""
        if self.attachment:
            return self.attachment.name.split('/')[-1]
        return ""
    
    def is_video_file(self):
        """Verifica si el attachment es un archivo de video."""
        if not self.attachment:
            return False
        video_extensions = ['.mp4', '.webm', '.mov', '.avi', '.mkv', '.m4v']
        file_name = self.attachment.name.lower()
        return any(file_name.endswith(ext) for ext in video_extensions)
    
    def get_file_size_mb(self):
        """Retorna el tamaño del archivo en MB."""
        if not self.attachment:
            return None
        try:
            size_bytes = self.attachment.size
            return round(size_bytes / (1024 * 1024), 2)
        except (AttributeError, OSError):
            return None
    
    def get_content_preview(self):
        """Retorna un preview del contenido según el tipo."""
        if self.content_type == "text":
            return self.text_content[:200] + "..." if len(self.text_content) > 200 else self.text_content
        elif self.content_type == "video":
            return f"Video: {self.video_url or 'Archivo subido'}"
        elif self.content_type in ["image", "file"]:
            return f"Archivo: {self.get_file_name()}"
        return ""

    class Meta:
        ordering = ("order", "id")
        unique_together = ("course", "order")


# =========================
# Enrollment (ACCESO REAL)
# =========================
class Enrollment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")
        ordering = ("-enrolled_at",)

    def __str__(self):
        return f"{self.user.username} -> {self.course.title}"


# =========================
# LessonProgress (tipo Udemy)
# =========================
class LessonProgress(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE
    )

    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    # SOLO para lecciones de video
    # En texto/imagen simplemente se ignora
    last_position_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Last watched position for video lessons (seconds)"
    )

    class Meta:
        unique_together = ("user", "lesson")
        ordering = ("lesson",)

    def mark_completed(self):
        """
        Marca la lección como completada sin permitir auto-uncheck
        """
        if not self.completed:
            self.completed = True
            self.completed_at = timezone.now()
            self.save()

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"


# =========================
# CourseRating (1–5 estrellas)
# =========================
class CourseRating(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.course.title} - {self.rating}★"


# =========================
# Comment (comentarios del curso)
# =========================
class Comment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

    class Meta:
        ordering = ("-created_at",)

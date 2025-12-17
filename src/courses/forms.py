from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Comment, Course, Lesson


class StyledFormMixin:
    """Agrega clases y placeholders coherentes a todos los campos."""

    field_placeholders: dict[str, str] = {}

    def _style_fields(self):
        for name, field in self.fields.items():
            classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{classes} input-control".strip()

            if isinstance(field.widget, forms.CheckboxInput):
                continue

            placeholder = self.field_placeholders.get(name) or field.label
            field.widget.attrs.setdefault("placeholder", placeholder)

            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 4)


class CourseForm(StyledFormMixin, forms.ModelForm):
    field_placeholders = {
        "title": "Nombre atractivo para tu curso",
        "description": "Describe los objetivos, requisitos y beneficios",
    }

    class Meta:
        model = Course
        fields = ["title", "description", "is_listed"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["is_listed"].label = "Visible en el catálogo"
        self.fields["title"].max_length = 200
        self.fields["description"].required = True
        self._style_fields()
    
    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if len(title) < 5:
            raise forms.ValidationError("El título debe tener al menos 5 caracteres.")
        if len(title) > 200:
            raise forms.ValidationError("El título no puede exceder 200 caracteres.")
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get("description", "").strip()
        if len(description) < 20:
            raise forms.ValidationError("La descripción debe tener al menos 20 caracteres.")
        return description


class LessonForm(StyledFormMixin, forms.ModelForm):
    field_placeholders = {
        "title": "Nombre claro para la lección",
        "text_content": "Contenido en formato texto (Markdown básico permitido)",
        "video_url": "https://…",
        "order": "1, 2, 3… según el flujo del curso",
    }

    class Meta:
        model = Lesson
        fields = [
            "title",
            "content_type",
            "text_content",
            "video_url",
            "attachment",
            "order",
        ]
        widgets = {
            "text_content": forms.Textarea(),
            "order": forms.HiddenInput(),  # Oculto, se calcula automáticamente
        }

    def clean_attachment(self):
        """Valida el tipo y tamaño de archivo según el content_type."""
        from django.conf import settings
        
        attachment = self.cleaned_data.get("attachment")
        content_type = self.cleaned_data.get("content_type")
        
        if attachment and content_type:
            # Extensiones permitidas por tipo
            video_extensions = ['.mp4', '.webm', '.mov', '.avi', '.mkv', '.m4v']
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
            file_extensions = ['.pdf', '.doc', '.docx', '.zip', '.rar', '.txt', '.xlsx', '.xls', '.pptx', '.ppt']
            
            file_name = attachment.name.lower()
            file_ext = None
            for ext in video_extensions + image_extensions + file_extensions:
                if file_name.endswith(ext):
                    file_ext = ext
                    break
            
            # Validar tipo de archivo
            if content_type == "video":
                if file_ext not in video_extensions:
                    raise forms.ValidationError(
                        "Por favor sube un video válido (MP4, WebM, MOV, AVI, MKV) o usa una URL de video."
                    )
                # Validar tamaño máximo de video (100 MB)
                if attachment.size > getattr(settings, 'MAX_VIDEO_SIZE', 100 * 1024 * 1024):
                    max_size_mb = getattr(settings, 'MAX_VIDEO_SIZE', 100 * 1024 * 1024) / (1024 * 1024)
                    raise forms.ValidationError(
                        f"El video es demasiado grande. Tamaño máximo: {max_size_mb:.0f} MB"
                    )
            elif content_type == "image":
                if file_ext not in image_extensions:
                    raise forms.ValidationError(
                        "Por favor sube una imagen válida (JPG, PNG, GIF, WEBP, SVG)."
                    )
                # Validar tamaño máximo de imagen (10 MB)
                if attachment.size > getattr(settings, 'MAX_IMAGE_SIZE', 10 * 1024 * 1024):
                    max_size_mb = getattr(settings, 'MAX_IMAGE_SIZE', 10 * 1024 * 1024) / (1024 * 1024)
                    raise forms.ValidationError(
                        f"La imagen es demasiado grande. Tamaño máximo: {max_size_mb:.0f} MB"
                    )
            elif content_type == "file":
                if file_ext not in file_extensions:
                    raise forms.ValidationError(
                        "Por favor sube un archivo válido (PDF, DOC, DOCX, ZIP, TXT, XLSX, PPTX, etc.)."
                    )
                # Validar tamaño máximo de archivo (50 MB)
                if attachment.size > getattr(settings, 'MAX_FILE_SIZE', 50 * 1024 * 1024):
                    max_size_mb = getattr(settings, 'MAX_FILE_SIZE', 50 * 1024 * 1024) / (1024 * 1024)
                    raise forms.ValidationError(
                        f"El archivo es demasiado grande. Tamaño máximo: {max_size_mb:.0f} MB"
                    )
        
        return attachment

    def clean(self):
        cleaned_data = super().clean()
        content_type = cleaned_data.get("content_type")
        text_content = cleaned_data.get("text_content", "").strip()
        video_url = cleaned_data.get("video_url", "").strip()
        attachment = cleaned_data.get("attachment")
        
        # Obtener la instancia existente si estamos editando
        instance = getattr(self, 'instance', None)
        has_existing_attachment = instance and instance.attachment and instance.attachment.name

        errors = {}

        # Validar contenido según el tipo
        if content_type == "text":
            if not text_content:
                errors["text_content"] = "Las lecciones de texto deben incluir contenido escrito."

        # Video puede ser URL o archivo subido (nuevo o existente)
        elif content_type == "video":
            if not video_url and not attachment and not has_existing_attachment:
                errors["video_url"] = "Las lecciones de video deben incluir una URL de video o un archivo de video subido."

        # Para imagen y archivo, se necesita un attachment (nuevo o existente)
        # IMPORTANTE: Si hay un attachment existente, no requerir uno nuevo
        # Esto permite cambiar el tipo de contenido sin perder el archivo
        elif content_type in {"file", "image"}:
            if not attachment and not has_existing_attachment:
                if content_type == "image":
                    errors["attachment"] = "Las lecciones de imagen requieren que subas una imagen."
                else:
                    errors["attachment"] = "Las lecciones de archivo requieren que subas un archivo."

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que order no sea requerido (se calcula automáticamente)
        self.fields["order"].required = False
        # Mejorar el widget de archivo con extensiones de video
        self.fields["attachment"].widget.attrs.update({
            "accept": ".mp4,.webm,.mov,.avi,.mkv,.m4v,.pdf,.doc,.docx,.zip,.jpg,.jpeg,.png,.gif,.webp,.txt,.xlsx,.xls,.pptx,.ppt",
            "class": "file-input"
        })
        self._style_fields()


class CommentForm(StyledFormMixin, forms.ModelForm):
    field_placeholders = {"content": "Comparte tu experiencia con este curso"}

    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4, "maxlength": 1000}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].max_length = 1000
        self._style_fields()
    
    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()
        if len(content) < 10:
            raise forms.ValidationError("El comentario debe tener al menos 10 caracteres.")
        if len(content) > 1000:
            raise forms.ValidationError("El comentario no puede exceder 1000 caracteres.")
        return content


class UserProfileForm(StyledFormMixin, forms.ModelForm):
    field_placeholders = {
        "first_name": "Tu nombre",
        "last_name": "Apellidos",
        "email": "correo@ejemplo.com",
    }

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        self._style_fields()


class SignupForm(StyledFormMixin, UserCreationForm):
    field_placeholders = {
        "username": "Tu usuario",
        "first_name": "Nombre",
        "last_name": "Apellidos",
        "email": "correo@ejemplo.com",
        "password1": "Contraseña segura",
        "password2": "Confirma la contraseña",
    }

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        # hide username from UI, it will be autogenerated
        self.fields["username"].required = False
        self.fields["username"].widget = forms.HiddenInput()
        self._style_fields()
        # Password widgets already styled, but add class manually
        for field in ("password1", "password2"):
            self.fields[field].widget.attrs["class"] = "input-control"
            self.fields[field].widget.attrs.setdefault(
                "placeholder", self.field_placeholders[field]
            )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if (
            email
            and get_user_model().objects.filter(email__iexact=email).exists()
        ):
            raise forms.ValidationError(
                "Ya existe una cuenta con este correo."
            )
        return email

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get("username")
        email = cleaned.get("email")
        if email:
            candidate = email.lower()
            user_model = get_user_model()
            suffix = 1
            unique_candidate = candidate
            while user_model.objects.filter(username=unique_candidate).exists():
                suffix += 1
                unique_candidate = f"{candidate}+{suffix}"
            cleaned["username"] = unique_candidate
            self.cleaned_data["username"] = unique_candidate
        return cleaned


class EmailLoginForm(StyledFormMixin, AuthenticationForm):
    field_placeholders = {
        "username": "correo@ejemplo.com",
        "password": "Contraseña",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Correo electrónico"
        # Cambiar el widget a EmailInput para mejor validación HTML5
        self.fields["username"].widget = forms.EmailInput(attrs={
            "class": "input-control",
            "placeholder": "correo@ejemplo.com",
            "autocomplete": "email"
        })
        # Mejorar el campo de contraseña
        self.fields["password"].widget = forms.PasswordInput(attrs={
            "class": "input-control",
            "placeholder": "Tu contraseña",
            "autocomplete": "current-password"
        })
        self._style_fields()

    def clean_username(self):
        """Convierte el email ingresado al username correspondiente."""
        email = self.cleaned_data.get("username")
        if email:
            User = get_user_model()
            try:
                # Buscar usuario por email (case-insensitive)
                user = User.objects.get(email__iexact=email)
                # Retornar el username real para la autenticación
                return user.username
            except User.DoesNotExist:
                # Si no existe, retornar el email tal cual para que Django muestre el error estándar
                return email
        return email

# 🎓 Plataforma de Cursos — Proyecto Final Fullstack 2

Una plataforma completa de aprendizaje en línea construida con **Django 5.2.x** y **PostgreSQL** que permite a los instructores crear y gestionar cursos multimedia, y a los estudiantes inscribirse, seguir su progreso y completar lecciones.

> **Proyecto**: Opción C — Plataforma de Cursos  
> **Framework**: Django 5.2.8  
> **Base de Datos**: PostgreSQL 16+  
> **Arquitectura**: 100% Class-Based Views (CBVs)

---

## 📋 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Funcionalidades Detalladas](#-funcionalidades-detalladas)
- [Requisitos del Sistema](#-requisitos-del-sistema)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Guía de Uso](#-guía-de-uso)
- [Arquitectura Técnica](#-arquitectura-técnica)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Testing](#-testing)
- [Despliegue](#-despliegue)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Características Principales

### Para Estudiantes 👨‍🎓
- **Exploración de cursos**: Catálogo completo con búsqueda y filtrado
- **Inscripción**: Sistema de inscripción/uninscripción en cursos
- **Dashboard personalizado**: Vista centralizada de todos los cursos inscritos con progreso
- **Seguimiento de progreso**: Sistema tipo Udemy que rastrea lecciones completadas
- **Materiales multimedia**: Acceso a videos, textos, imágenes y archivos descargables
- **Comentarios**: Sistema de comentarios para interactuar con otros estudiantes
- **Reproductor de video**: Soporte para videos subidos (HTML5) y embeds de YouTube/Vimeo

### Para Instructores 👨‍🏫
- **Creación de cursos**: CRUD completo para crear, editar y eliminar cursos
- **Gestión de lecciones**: Crear lecciones con diferentes tipos de contenido
- **Reordenamiento visual**: Drag-and-drop para reordenar lecciones sin numeración manual
- **Subida de archivos**: Soporte para videos (MP4, WebM, MOV), imágenes (JPG, PNG, GIF) y documentos (PDF, ZIP, DOC)
- **Control de acceso**: Gestionar quién puede inscribirse en tus cursos
- **Estadísticas**: Ver número de estudiantes inscritos y lecciones por curso

### Requisitos Técnicos Cumplidos 
- ✅ **Django 5.2.x** (versión 5.2.8)
- ✅ **PostgreSQL 16+** (no SQLite en producción)
- ✅ **Django Auth** integrado con login/logout/signup y perfil de usuario
- ✅ **100% Class-Based Views (CBVs)** - Todas las vistas son CBVs
- ✅ **10+ tests** unitarios e integración
- ✅ **Dockerfile** funcional con Python 3.11
- ✅ **docker-compose.yml** con servicios web + db
- ✅ **Variables de entorno (.env)** para configuración
- ✅ **UUID** para identificadores de cursos (seguridad y escalabilidad)
- ✅ **Cloud Storage** configurable (OCI Object Storage, AWS S3)

---

## 🚀 Funcionalidades Detalladas

### 1. Sistema de Cursos

#### Crear un Curso
- Cualquier usuario autenticado puede crear cursos
- Campos requeridos: título y descripción
- El creador se convierte automáticamente en instructor
- Identificador único con UUID (no secuencial)

#### Gestionar Cursos
- **Editar**: Modificar título y descripción
- **Eliminar**: Eliminar curso y todas sus lecciones asociadas
- **Visibilidad**: Controlar si el curso acepta nuevas inscripciones (`is_listed`)

### 2. Sistema de Lecciones

#### Tipos de Contenido Soportados

1. **📝 Texto**
   - Contenido en texto plano con formato de líneas
   - Ideal para material de lectura

2. **🎥 Video**
   - **Videos subidos**: MP4, WebM, MOV, AVI, MKV (máx. 100MB)
   - **Videos embebidos**: URLs de YouTube o Vimeo (conversión automática a embed)
   - Reproductor HTML5 con controles completos

3. **🖼️ Imagen**
   - Formatos: JPG, PNG, GIF, WEBP, SVG (máx. 10MB)
   - Visualización optimizada con opción de descarga

4. **📄 Archivo**
   - Documentos: PDF, DOC, DOCX, ZIP, TXT, XLSX, PPTX (máx. 50MB)
   - Descarga directa con información del archivo

#### Gestión de Lecciones
- **Crear**: Agregar lecciones a un curso (solo instructores)
- **Editar**: Modificar contenido, tipo y archivos adjuntos
- **Eliminar**: Eliminar lección (archivos se eliminan automáticamente del storage)
- **Reordenar**: Drag-and-drop visual para cambiar el orden sin conflictos

### 3. Sistema de Progreso

- **Marcar como completada**: Los estudiantes pueden marcar lecciones como completadas
- **Progreso por curso**: Cálculo automático del porcentaje de avance
- **Dashboard**: Vista consolidada de todos los cursos con barras de progreso
- **Historial**: Fecha y hora de completación de cada lección

### 4. Sistema de Inscripciones

- **Inscribirse**: Cualquier usuario puede inscribirse en cursos públicos
- **Desinscribirse**: Los estudiantes pueden salir de un curso
- **Restricciones**: Los instructores no pueden inscribirse en sus propios cursos
- **Acceso**: Solo estudiantes inscritos pueden ver el contenido de las lecciones

### 5. Sistema de Comentarios

- **Comentar**: Estudiantes inscritos pueden dejar comentarios en cursos
- **Visualización**: Comentarios ordenados por fecha (más recientes primero)
- **Autenticación**: Requiere estar inscrito en el curso

### 6. Autenticación y Perfiles

- **Registro**: Formulario de signup con validación
- **Login**: Autenticación por email (no username)
- **Perfil**: Editar información personal
- **Sesión**: Sistema de sesiones de Django

---

## 💻 Requisitos del Sistema

### Desarrollo Local
- **Python**: 3.11 o superior
- **PostgreSQL**: 16+ (o SQLite para desarrollo rápido)
- **Docker**: 20.10+ (opcional pero recomendado)
- **docker-compose**: 2.0+ (opcional pero recomendado)

### Producción
- **Servidor**: Ubuntu 20.04+ / Debian 11+ / Oracle Linux 8+
- **Docker**: 20.10+
- **Nginx**: 1.18+ (para proxy inverso)
- **PostgreSQL**: 16+ (o servicio gestionado)
- **Cloud Storage**: OCI Object Storage o AWS S3 (recomendado)

---

## 🔧 Instalación y Configuración

### Opción 1: Docker (Recomendado)

#### Paso 1: Clonar el Repositorio
```bash
git clone <tu-repositorio>
cd fs2Project
```

#### Paso 2: Configurar Variables de Entorno
Crea el archivo `src/.env` basándote en `.env.example`:

```bash
# Django Settings
SECRET_KEY=tu-clave-secreta-super-segura-aqui
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000

# Database Configuration (PostgreSQL)
POSTGRES_DB=fs2_courses
POSTGRES_USER=fs2_user
POSTGRES_PASSWORD=fs2_password_segura
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Optional: Use SQLite for local development (set to 1 to enable)
DJANGO_USE_SQLITE=0

# Cloud Storage (OCI Object Storage) - Para producción
USE_CLOUD_STORAGE=0  # Cambiar a 1 en producción
# AWS_ACCESS_KEY_ID=tu-access-key-id
# AWS_SECRET_ACCESS_KEY=tu-secret-key
# AWS_STORAGE_BUCKET_NAME=nombre-bucket
# AWS_S3_REGION_NAME=us-ashburn-1
# AWS_S3_ENDPOINT_URL=https://tu-namespace.compat.objectstorage.region.oraclecloud.com
```

#### Paso 3: Construir y Levantar Servicios
```bash
docker-compose up --build
```

#### Paso 4: Crear Superusuario
En otra terminal:
```bash
docker-compose exec web python manage.py createsuperuser
```

#### Paso 5: Acceder a la Aplicación
- **Aplicación**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/

### Opción 2: Instalación Local (sin Docker)

#### Paso 1: Crear Entorno Virtual
```bash
python3.11 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

#### Paso 2: Instalar Dependencias
```bash
pip install -r requirements.txt
```

#### Paso 3: Configurar Base de Datos
```bash
# Opción A: PostgreSQL (recomendado)
# Asegúrate de tener PostgreSQL instalado y crear una base de datos

# Opción B: SQLite (solo desarrollo)
export DJANGO_USE_SQLITE=1
```

#### Paso 4: Configurar Variables de Entorno
Crea `src/.env` (ver sección anterior)

#### Paso 5: Aplicar Migraciones
```bash
cd src
python manage.py migrate
```

#### Paso 6: Crear Superusuario
```bash
python manage.py createsuperuser
```

#### Paso 7: Ejecutar Servidor
```bash
python manage.py runserver
```

La aplicación estará disponible en http://localhost:8000

---

## 📖 Guía de Uso

### Para Estudiantes

#### 1. Registrarse e Iniciar Sesión
1. Ve a la página de inicio
2. Haz clic en "Registrarse" o "Ingresar"
3. Completa el formulario de registro (email y contraseña)
4. Inicia sesión con tu email

#### 2. Explorar Cursos
1. En la página principal verás el catálogo de cursos
2. Usa la barra de búsqueda para filtrar por título o descripción
3. Haz clic en un curso para ver detalles

#### 3. Inscribirse en un Curso
1. Ve a la página de detalle del curso
2. Haz clic en el botón "Inscribirse en este curso"
3. Serás redirigido al dashboard donde verás el curso

#### 4. Tomar Lecciones
1. Desde el dashboard o la página del curso, haz clic en una lección
2. Visualiza el contenido (texto, video, imagen o archivo)
3. Al finalizar, haz clic en "✅ Marcar como completada"
4. Tu progreso se actualizará automáticamente

#### 5. Ver Progreso
1. Ve a "Mi Tablero" desde el menú
2. Verás todos tus cursos inscritos con:
   - Porcentaje de progreso
   - Número de lecciones completadas
   - Barra de progreso visual

#### 6. Comentar en Cursos
1. En la página de detalle del curso (debes estar inscrito)
2. Escribe un comentario en el formulario
3. Tu comentario aparecerá en la lista

### Para Instructores

#### 1. Crear un Curso
1. Inicia sesión
2. Haz clic en "➕ Publicar nuevo curso" o ve a `/courses/create/`
3. Completa el formulario:
   - **Título**: Nombre del curso
   - **Descripción**: Descripción detallada
4. Haz clic en "Crear curso"
5. Serás redirigido a la página del curso

#### 2. Agregar Lecciones
1. En la página de tu curso, haz clic en "➕ Agregar lección"
2. Completa el formulario:
   - **Título**: Nombre de la lección
   - **Tipo de contenido**: Selecciona Texto, Video, Imagen o Archivo
   - **Contenido**: Dependiendo del tipo:
     - **Texto**: Escribe el contenido
     - **Video**: Sube un archivo o pega URL de YouTube/Vimeo
     - **Imagen**: Sube una imagen
     - **Archivo**: Sube un documento
3. El orden se calcula automáticamente (no necesitas especificarlo)
4. Haz clic en "Crear lección"

#### 3. Reordenar Lecciones
1. En la página de tu curso, verás todas las lecciones
2. **Modo instructor activado**: Verás un mensaje indicando que puedes arrastrar
3. Haz clic y arrastra una lección a la posición deseada
4. El orden se guarda automáticamente

#### 4. Editar Lecciones
1. Haz clic en el botón "✏️ Editar" junto a una lección
2. Modifica el contenido, tipo o archivo
3. **Nota**: Si cambias el archivo, el anterior se eliminará automáticamente
4. Haz clic en "Guardar cambios"

#### 5. Eliminar Lecciones
1. Haz clic en el botón "🗑️ Eliminar" junto a una lección
2. Confirma la eliminación
3. El archivo asociado se eliminará automáticamente del storage

#### 6. Gestionar el Curso
- **Editar**: Haz clic en "Editar curso" para modificar título/descripción
- **Eliminar**: Haz clic en "Eliminar curso" (eliminará todas las lecciones)
- **Visibilidad**: Controla si el curso acepta nuevas inscripciones

---

## 🏗️ Arquitectura Técnica

### Backend

#### Framework y Versiones
- **Django**: 5.2.8
- **Python**: 3.11
- **PostgreSQL**: 16+
- **Gunicorn**: 23.0.0 (servidor WSGI para producción)

#### Patrón de Vistas
- **100% Class-Based Views (CBVs)**: Todas las vistas heredan de Django CBVs
- **Mixins personalizados**: `CourseInstructorMixin`, `StaffRequiredMixin`
- **Vistas principales**:
  - `ListView`: Catálogo de cursos
  - `DetailView`: Detalle de curso y lección
  - `CreateView`: Crear curso, lección, inscripción, comentario
  - `UpdateView`: Editar curso y lección
  - `DeleteView`: Eliminar curso, lección, inscripción
  - `TemplateView`: Dashboard de estudiantes
  - `View`: Progreso de lecciones, reordenamiento

#### Autenticación
- **Sistema**: `django.contrib.auth`
- **Login**: Por email (no username)
- **Formularios personalizados**: `EmailLoginForm`, `SignupForm`
- **Protección**: `LoginRequiredMixin` en vistas protegidas

#### Base de Datos

**Modelos principales**:

1. **Course**
   - `identifier`: UUID (único, no secuencial)
   - `instructor`: ForeignKey a User
   - `title`, `description`: Información del curso
   - `is_listed`: Control de visibilidad
   - `created_at`: Timestamp

2. **Lesson**
   - `course`: ForeignKey a Course
   - `title`: Título de la lección
   - `content_type`: Text, Video, Image, File
   - `text_content`: Contenido de texto (opcional)
   - `video_url`: URL de video externo (opcional)
   - `attachment`: Archivo subido (opcional)
   - `order`: PositiveIntegerField (único por curso)
   - **Métodos**: `get_video_embed_url()`, `get_file_name()`, `is_video_file()`

3. **Enrollment**
   - `user`: ForeignKey a User
   - `course`: ForeignKey a Course
   - `enrolled_at`: Timestamp
   - **Unique constraint**: (user, course)

4. **LessonProgress**
   - `user`: ForeignKey a User
   - `lesson`: ForeignKey a Lesson
   - `completed`: Boolean
   - `completed_at`: DateTime (nullable)
   - `last_position_seconds`: Para videos (futuro)
   - **Método**: `mark_completed()`

5. **Comment**
   - `user`: ForeignKey a User
   - `course`: ForeignKey a Course
   - `content`: TextField
   - `created_at`: Timestamp

6. **CourseRating**
   - `user`: ForeignKey a User
   - `course`: ForeignKey a Course
   - `rating`: PositiveSmallIntegerField (1-5)
   - `created_at`: Timestamp

#### Almacenamiento de Archivos

**Desarrollo**:
- Archivos en `src/media/lessons/YYYY/MM/DD/`
- Servidos por Django development server

**Producción**:
- **OCI Object Storage**: Compatible con S3 API
- **AWS S3**: Alternativa
- **Configuración**: `django-storages` + `boto3`
- **Eliminación automática**: Archivos se eliminan cuando se actualiza/elimina lección

### Frontend

#### Templates
- **Motor**: Django Templates con herencia
- **Base template**: `base.html` con navegación y estructura común
- **Templates principales**:
  - `course_list.html`: Catálogo con búsqueda
  - `course_detail.html`: Detalle con lecciones y drag-and-drop
  - `course_form.html`: Crear/editar curso
  - `lesson_detail.html`: Visualización de lección
  - `lesson_form.html`: Crear/editar lección
  - `dashboard.html`: Tablero de estudiantes
  - `login.html`, `signup.html`: Autenticación

#### CSS
- **Archivo**: `src/courses/static/courses/style.css`
- **Estilo**: Moderno con gradientes, glassmorphism, responsive design
- **Características**:
  - Diseño responsive (mobile-first)
  - Animaciones suaves
  - Estados hover y focus
  - Estilos para drag-and-drop
  - Reproductor de video responsive

#### JavaScript
- **Vanilla JS**: Sin frameworks externos
- **Funcionalidades**:
  - Drag-and-drop para reordenar lecciones
  - Mostrar/ocultar campos según tipo de contenido
  - Mostrar nombre de archivo al seleccionar
  - Validación de formularios en cliente

### Seguridad

- **CSRF Protection**: Tokens CSRF en todos los formularios
- **SQL Injection**: Prevenido por Django ORM
- **XSS**: Escapado automático en templates
- **Autenticación**: Sistema robusto de Django
- **Permisos**: Mixins para control de acceso
- **UUID**: Identificadores no secuenciales (seguridad)

---

## 📁 Estructura del Proyecto

```
fs2Project/
├── src/                          # Código fuente principal
│   ├── app/                      # Configuración de Django
│   │   ├── settings.py           # Configuración principal
│   │   ├── urls.py               # URLs principales
│   │   ├── wsgi.py               # WSGI para producción
│   │   └── asgi.py               # ASGI (futuro)
│   │
│   ├── courses/                  # Aplicación principal
│   │   ├── models.py             # Modelos de datos
│   │   ├── views.py              # Vistas (CBVs)
│   │   ├── forms.py              # Formularios
│   │   ├── urls.py               # URLs de la app
│   │   ├── admin.py              # Configuración de admin
│   │   ├── tests.py              # Tests unitarios
│   │   │
│   │   ├── migrations/          # Migraciones de BD
│   │   │
│   │   ├── templates/            # Templates HTML
│   │   │   ├── base.html
│   │   │   ├── courses/          # Templates de cursos
│   │   │   └── registration/    # Templates de auth
│   │   │
│   │   └── static/               # Archivos estáticos
│   │       └── courses/
│   │           └── style.css
│   │
│   ├── media/                    # Archivos subidos (desarrollo)
│   ├── staticfiles/              # Archivos estáticos recopilados
│   ├── manage.py                 # Script de gestión de Django
│   └── .env                      # Variables de entorno (NO subir a Git)
│
├── docker-compose.yml            # Configuración de Docker Compose
├── Dockerfile                    # Imagen de Docker
├── requirements.txt              # Dependencias de Python
├── README.md                     # Este archivo
├── DEPLOYMENT.md                 # Guía de despliegue
├── OCI_OBJECT_STORAGE_SETUP.md  # Guía de OCI Object Storage
└── .env.example                  # Ejemplo de variables de entorno
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Con Docker
docker-compose exec web python manage.py test

# Localmente
DJANGO_USE_SQLITE=1 python manage.py test
```

### Cobertura de Tests

Los tests cubren:

1. **Búsqueda de cursos**: Filtrado por título/descripción
2. **Inscripciones**: Crear y eliminar inscripciones
3. **Restricciones**: Instructores no pueden inscribirse en sus cursos
4. **Progreso**: Marcado de lecciones como completadas
5. **Permisos**: Acceso a lecciones solo para inscritos
6. **Comentarios**: Requieren inscripción
7. **Validaciones**: Formularios validan contenido requerido
8. **Dashboard**: Cálculo correcto de porcentaje de progreso

### Ejecutar Tests Específicos

```bash
# Test de un modelo específico
python manage.py test courses.tests.CoursePlatformTests.test_course_list_search_filters_results

# Test de una app completa
python manage.py test courses
```

---

## 🚀 Despliegue

### Guías Disponibles

1. **[DEPLOYMENT.md](DEPLOYMENT.md)**: Guía completa de despliegue en OCI
   - Configuración de servidor
   - Nginx como proxy inverso
   - SSL/HTTPS con Let's Encrypt
   - Variables de entorno de producción

2. **[OCI_OBJECT_STORAGE_SETUP.md](OCI_OBJECT_STORAGE_SETUP.md)**: Configuración de OCI Object Storage
   - Crear bucket
   - Generar credenciales
   - Configurar variables de entorno
   - Verificar funcionamiento

### Resumen Rápido de Despliegue

1. **Preparar servidor OCI** con Docker instalado
2. **Clonar proyecto** desde GitHub
3. **Configurar `.env`** con variables de producción:
   - `DEBUG=0`
   - `ALLOWED_HOSTS` con tu dominio
   - Credenciales de PostgreSQL
   - Credenciales de OCI Object Storage
4. **Configurar Cloud Storage** (ver `OCI_OBJECT_STORAGE_SETUP.md`)
5. **Levantar servicios**: `docker-compose up -d`
6. **Configurar Nginx** y SSL (ver `DEPLOYMENT.md`)
7. **Apuntar dominio** al servidor

### Almacenamiento en Producción

**Recomendado**: OCI Object Storage o AWS S3

**Ventajas**:
- Escalabilidad ilimitada
- CDN opcional para mejor rendimiento
- Redundancia y backup automático
- Costos por uso

**Configuración**:
```bash
USE_CLOUD_STORAGE=1
AWS_ACCESS_KEY_ID=tu-access-key-id
AWS_SECRET_ACCESS_KEY=tu-secret-key
AWS_STORAGE_BUCKET_NAME=nombre-bucket
AWS_S3_REGION_NAME=us-ashburn-1
AWS_S3_ENDPOINT_URL=https://tu-namespace.compat.objectstorage.region.oraclecloud.com
```

---

## 🔍 Troubleshooting

### Problemas Comunes

#### 1. Error de conexión a PostgreSQL
```
django.db.utils.OperationalError: connection failed
```

**Solución**:
- Verifica que PostgreSQL esté corriendo: `docker-compose ps`
- Revisa las variables de entorno en `src/.env`
- Asegúrate de que `POSTGRES_HOST=db` (nombre del servicio en Docker)

#### 2. Archivos no aparecen en OCI Object Storage
```
File not found error
```

**Solución**:
- Verifica que `USE_CLOUD_STORAGE=1` en `.env`
- Confirma que las credenciales son correctas
- Revisa que el bucket existe y tiene permisos públicos
- Verifica `AWS_S3_ENDPOINT_URL` (debe incluir el namespace)

#### 3. Error de migraciones
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Solución**:
```bash
# Resetear migraciones (CUIDADO: pérdida de datos)
docker-compose exec web python manage.py migrate --fake-initial

# O aplicar migraciones normalmente
docker-compose exec web python manage.py migrate
```

#### 4. Error de UniqueViolation al reordenar lecciones
```
UniqueViolation: duplicate key value violates unique constraint
```

**Solución**: Ya está resuelto en el código. Si persiste:
- Verifica que estás usando la versión más reciente
- El sistema usa valores temporales altos para evitar conflictos

#### 5. Archivos no se eliminan de OCI
```
File remains in bucket after lesson deletion
```

**Solución**:
- Verifica que `django-storages` esté instalado: `pip list | grep django-storages`
- Revisa los logs: `docker-compose logs web`
- El código maneja errores silenciosamente (revisa logs para warnings)

#### 6. Error 500 en producción
```
Internal Server Error
```

**Solución**:
- Revisa logs: `docker-compose logs web`
- Verifica `DEBUG=0` y `ALLOWED_HOSTS` configurado
- Asegúrate de que `collectstatic` se ejecutó
- Revisa permisos de archivos

### Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f web

# Reiniciar servicios
docker-compose restart

# Reconstruir imágenes
docker-compose up --build

# Acceder a shell de Django
docker-compose exec web python manage.py shell

# Crear migraciones
docker-compose exec web python manage.py makemigrations

# Aplicar migraciones
docker-compose exec web python manage.py migrate

# Recopilar archivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Crear superusuario
docker-compose exec web python manage.py createsuperuser
```

---

## 📚 Recursos Adicionales

### Documentación Oficial
- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [OCI Object Storage Documentation](https://docs.oracle.com/en-us/iaas/Content/Object/Concepts/objectstorageoverview.htm)

### Guías del Proyecto
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Despliegue completo en OCI
- **[OCI_OBJECT_STORAGE_SETUP.md](OCI_OBJECT_STORAGE_SETUP.md)**: Configuración de almacenamiento

---

## 📝 Licencia

Este proyecto fue desarrollado como parte del Proyecto Final de Desarrollo Web Fullstack 2.

---

## 👥 Contribuciones

Este es un proyecto académico. Para mejoras o correcciones, por favor abre un issue o pull request.

---

## 🎯 Próximas Mejoras (Futuro)

- [ ] Sistema de calificaciones (ratings) funcional en UI
- [ ] Búsqueda avanzada con filtros
- [ ] Notificaciones por email
- [ ] Certificados de finalización
- [ ] Sistema de categorías/tags
- [ ] Preview de videos antes de subir
- [ ] Compresión automática de imágenes
- [ ] Analytics para instructores

---


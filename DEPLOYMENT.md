# Guía de Despliegue en Producción

Esta guía explica cómo desplegar la plataforma de cursos en producción, incluyendo la configuración de almacenamiento de archivos multimedia.

## 📋 Tabla de Contenidos

1. [Opciones de Almacenamiento](#opciones-de-almacenamiento)
2. [Despliegue en OCI](#despliegue-en-oci)
3. [Configuración de Cloud Storage](#configuración-de-cloud-storage)
4. [Configuración con Nginx](#configuración-con-nginx)
5. [SSL/HTTPS](#sslhttps)

---

## 🗄️ Opciones de Almacenamiento

Para archivos multimedia (videos, imágenes, documentos) en producción, tienes 3 opciones:

### Opción 1: OCI Object Storage (Recomendado) ⭐

**Ventajas:**
- ✅ Escalable e ilimitado
- ✅ CDN integrado
- ✅ Optimizado para videos grandes
- ✅ Compatible con S3 API
- ✅ Costo bajo

**Configuración:**
1. Crear un bucket en OCI Object Storage
2. Generar credenciales de acceso (Access Key + Secret Key)
3. Configurar variables de entorno (ver abajo)

### Opción 2: Almacenamiento Local con Nginx

**Ventajas:**
- ✅ Simple de configurar
- ✅ Sin costos adicionales
- ✅ Control total

**Desventajas:**
- ⚠️ Limitado por espacio del servidor
- ⚠️ Puede ser lento para videos grandes
- ⚠️ No escalable

### Opción 3: AWS S3 u otro servicio S3-compatible

**Ventajas:**
- ✅ Similar a OCI Object Storage
- ✅ Muy popular y documentado

---

## 🚀 Despliegue en OCI

### Paso 1: Preparar el Servidor

```bash
# Conectar por SSH a tu VM en OCI
ssh usuario@tu-servidor-ip

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker y Docker Compose
sudo apt install -y docker.io docker-compose git
sudo systemctl enable docker
sudo systemctl start docker

# Agregar tu usuario al grupo docker
sudo usermod -aG docker $USER
```

### Paso 2: Clonar el Proyecto

```bash
# Clonar desde GitHub
git clone tu-repositorio-github
cd fs2Project

# Crear archivo .env de producción
nano src/.env
```

### Paso 3: Configurar Variables de Entorno

Edita `src/.env` con estos valores:

```bash
# Django Settings
SECRET_KEY=tu-clave-secreta-super-segura-aqui
DEBUG=0
ALLOWED_HOSTS=tu-dominio.jcarlos19.com,www.tu-dominio.jcarlos19.com
CSRF_TRUSTED_ORIGINS=https://tu-dominio.jcarlos19.com,https://www.tu-dominio.jcarlos19.com

# Database
POSTGRES_DB=proyecto
POSTGRES_USER=usuario
POSTGRES_PASSWORD=password-super-seguro
POSTGRES_HOST=db
POSTGRES_PORT=5432
DJANGO_USE_SQLITE=0

# Cloud Storage (si usas OCI Object Storage o S3)
USE_CLOUD_STORAGE=1
AWS_ACCESS_KEY_ID=tu-access-key-id
AWS_SECRET_ACCESS_KEY=tu-secret-access-key
AWS_STORAGE_BUCKET_NAME=nombre-de-tu-bucket
AWS_S3_REGION_NAME=us-ashburn-1
AWS_S3_ENDPOINT_URL=https://namespace.compat.objectstorage.us-ashburn-1.oraclecloud.com
```

### Paso 4: Levantar la Aplicación

```bash
# Construir y levantar servicios
docker-compose up -d --build

# Aplicar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Recopilar archivos estáticos
docker-compose exec web python manage.py collectstatic --noinput
```

---

## ☁️ Configuración de Cloud Storage

### Para OCI Object Storage:

1. **Crear Bucket en OCI:**
   - Ve a OCI Console → Object Storage → Buckets
   - Crea un nuevo bucket (ej: `miapp-media`)
   - Configura como público si quieres acceso directo

2. **Generar Credenciales:**
   - Ve a Identity → Users → Tu usuario
   - API Keys → Generate API Key
   - Guarda el Access Key ID y Secret Access Key

3. **Configurar Variables en .env:**
   ```bash
   USE_CLOUD_STORAGE=1
   AWS_ACCESS_KEY_ID=tu-access-key-id-de-oci
   AWS_SECRET_ACCESS_KEY=tu-secret-key-de-oci
   AWS_STORAGE_BUCKET_NAME=miapp-media
   AWS_S3_REGION_NAME=us-ashburn-1  # Tu región de OCI
   AWS_S3_ENDPOINT_URL=https://tu-namespace.compat.objectstorage.us-ashburn-1.oraclecloud.com
   ```

4. **Reiniciar la aplicación:**
   ```bash
   docker-compose restart web
   ```

### Para AWS S3:

```bash
USE_CLOUD_STORAGE=1
AWS_ACCESS_KEY_ID=tu-aws-access-key
AWS_SECRET_ACCESS_KEY=tu-aws-secret-key
AWS_STORAGE_BUCKET_NAME=tu-bucket-name
AWS_S3_REGION_NAME=us-east-1
# No necesitas AWS_S3_ENDPOINT_URL para AWS S3
```

### Para Almacenamiento Local (sin cloud):

```bash
USE_CLOUD_STORAGE=0
# Los archivos se guardarán en src/media/
```

---

## 🌐 Configuración con Nginx

### Instalar Nginx

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

### Configurar Nginx

Crea `/etc/nginx/sites-available/miapp`:

```nginx
server {
    listen 80;
    server_name tu-dominio.jcarlos19.com;

    # Redirigir HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.jcarlos19.com;

    # Certificados SSL (se generan con certbot)
    ssl_certificate /etc/letsencrypt/live/tu-dominio.jcarlos19.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.jcarlos19.com/privkey.pem;

    # Configuración SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Tamaño máximo de archivo (importante para videos)
    client_max_body_size 100M;

    # Proxy a Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Servir archivos media directamente (si no usas cloud storage)
    location /media/ {
        alias /ruta/a/tu/proyecto/src/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Servir archivos estáticos
    location /static/ {
        alias /ruta/a/tu/proyecto/src/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### Activar el sitio

```bash
sudo ln -s /etc/nginx/sites-available/miapp /etc/nginx/sites-enabled/
sudo nginx -t  # Verificar configuración
sudo systemctl reload nginx
```

---

## 🔒 SSL/HTTPS

### Obtener Certificado SSL con Let's Encrypt

```bash
# Obtener certificado
sudo certbot --nginx -d tu-dominio.jcarlos19.com

# Renovación automática (ya está configurada)
sudo certbot renew --dry-run
```

---

## 📊 Monitoreo y Mantenimiento

### Ver logs

```bash
# Logs de la aplicación
docker-compose logs -f web

# Logs de la base de datos
docker-compose logs -f db

# Logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Backup de Base de Datos

```bash
# Crear backup
docker-compose exec db pg_dump -U usuario proyecto > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker-compose exec -T db psql -U usuario proyecto < backup_20241215.sql
```

### Actualizar la Aplicación

```bash
# Pull cambios de GitHub
git pull origin main

# Reconstruir y reiniciar
docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

---

## 🎯 Checklist de Despliegue

- [ ] Servidor OCI configurado con Docker
- [ ] Dominio apuntando a la IP del servidor
- [ ] Variables de entorno configuradas en `.env`
- [ ] Base de datos PostgreSQL funcionando
- [ ] Cloud Storage configurado (OCI Object Storage o S3)
- [ ] Nginx configurado como proxy inverso
- [ ] Certificado SSL instalado (HTTPS)
- [ ] Superusuario creado
- [ ] Migraciones aplicadas
- [ ] Archivos estáticos recopilados
- [ ] Pruebas de subida de archivos funcionando

---

## 💡 Tips Importantes

1. **Videos grandes:** Usa siempre cloud storage (OCI Object Storage o S3) para videos
2. **Seguridad:** Nunca subas el archivo `.env` a GitHub
3. **Backups:** Configura backups automáticos de la base de datos
4. **Monitoreo:** Considera usar herramientas de monitoreo (opcional)
5. **CDN:** Si usas OCI Object Storage, puedes configurar un CDN para mejor rendimiento

---

## 🆘 Solución de Problemas

### Los archivos no se suben
- Verifica permisos del directorio `media/`
- Verifica configuración de cloud storage
- Revisa logs: `docker-compose logs web`

### Videos no se reproducen
- Verifica que el bucket tenga permisos públicos
- Verifica la configuración de CORS en el bucket
- Revisa que las URLs de media estén correctas

### Error 413 (Request Entity Too Large)
- Aumenta `client_max_body_size` en Nginx
- Verifica límites en Django settings

---

¿Necesitas ayuda con algún paso específico? Revisa los logs y la documentación de OCI Object Storage.


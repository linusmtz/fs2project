# 🚀 Guía de Deployment con Docker

Esta guía explica cómo deployar la aplicación en tu VM de Oracle Cloud usando Docker y Nginx.

## 📋 Prerrequisitos

- ✅ Docker instalado (`docker.io`)
- ✅ Docker Compose instalado (`docker-compose-plugin`)
- ✅ Nginx instalado y funcionando
- ✅ Dominio configurado: `app.linusmartinez.com`
- ✅ GitHub Actions self-hosted runner configurado

## 🔧 Configuración Inicial

### 1. Configurar Nginx

Ejecuta el script de configuración:

```bash
chmod +x setup-nginx.sh
sudo ./setup-nginx.sh
```

O manualmente:

```bash
# Copiar configuración de Nginx
sudo cp nginx/app.linusmartinez.com.conf /etc/nginx/sites-available/app.linusmartinez.com

# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/app.linusmartinez.com /etc/nginx/sites-enabled/

# Verificar y recargar
sudo nginx -t
sudo systemctl reload nginx
```

### 2. Crear archivo `.env`

Copia el ejemplo y configura tus variables:

```bash
cd /home/ubuntu/fs2Project
cp .env.example src/.env
nano src/.env  # Editar con tus valores reales
```

**Variables importantes:**
- `SECRET_KEY`: Genera una nueva con `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `ALLOWED_HOSTS`: Debe incluir `app.linusmartinez.com`
- `CSRF_TRUSTED_ORIGINS`: Debe incluir `http://app.linusmartinez.com`
- `POSTGRES_PASSWORD`: Password segura para PostgreSQL
- Credenciales de OCI Object Storage

### 3. Configurar GitHub Actions Runner

Si aún no tienes el runner configurado:

1. Ve a tu repositorio en GitHub → Settings → Actions → Runners
2. Agrega un nuevo self-hosted runner
3. Sigue las instrucciones para instalarlo en tu VM
4. Asegúrate de que el label sea `self-hosted` (o actualiza el workflow)

## 🚀 Deployment Automático

### Con GitHub Actions (Recomendado)

1. **Push a main/master**: El workflow se ejecutará automáticamente
2. **Manual**: Ve a Actions → Deploy to Production → Run workflow

El workflow:
- ✅ Actualiza el código desde GitHub
- ✅ Construye las imágenes Docker
- ✅ Levanta los contenedores
- ✅ Ejecuta migraciones
- ✅ Recopila archivos estáticos
- ✅ Verifica que todo esté funcionando

### Deployment Manual

Si prefieres hacerlo manualmente:

```bash
cd /home/ubuntu/fs2Project
chmod +x deploy.sh
./deploy.sh
```

## 📁 Estructura de Directorios

```
/home/ubuntu/fs2Project/
├── docker-compose.prod.yml  # Configuración de producción
├── Dockerfile                # Imagen de la aplicación
├── src/
│   ├── .env                  # Variables de entorno (¡NO subir a Git!)
│   ├── app/
│   ├── courses/
│   └── manage.py
├── .github/
│   └── workflows/
│       └── deploy.yml        # Workflow de GitHub Actions
└── nginx/
    └── app.linusmartinez.com.conf  # Configuración de Nginx
```

## 🔍 Verificación

### Verificar contenedores

```bash
cd /home/ubuntu/fs2Project
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs web
docker compose -f docker-compose.prod.yml logs db
```

### Verificar aplicación

```bash
# Desde la VM
curl http://localhost:8000

# Desde fuera
curl http://app.linusmartinez.com
```

### Verificar Nginx

```bash
sudo nginx -t
sudo systemctl status nginx
```

## 🛠️ Comandos Útiles

### Reiniciar servicios

```bash
cd /home/ubuntu/fs2Project
docker compose -f docker-compose.prod.yml restart web
```

### Ver logs en tiempo real

```bash
docker compose -f docker-compose.prod.yml logs -f web
```

### Ejecutar comandos Django

```bash
# Crear superusuario
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Migraciones
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Shell de Django
docker compose -f docker-compose.prod.yml exec web python manage.py shell
```

### Detener todo

```bash
docker compose -f docker-compose.prod.yml down
```

### Reconstruir desde cero

```bash
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

## 🔒 Seguridad

### Firewall

Asegúrate de que solo el puerto 80 esté abierto:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

### Variables de Entorno

- ✅ **NUNCA** subas `src/.env` a Git
- ✅ Usa `.gitignore` para excluirlo
- ✅ Genera `SECRET_KEY` único para producción
- ✅ Usa passwords fuertes para PostgreSQL

## 🐛 Troubleshooting

### Los contenedores no inician

```bash
# Ver logs
docker compose -f docker-compose.prod.yml logs

# Verificar .env
cat src/.env

# Verificar puertos
sudo netstat -tlnp | grep 8000
```

### Nginx no conecta con Docker

```bash
# Verificar que el contenedor está corriendo
docker compose -f docker-compose.prod.yml ps

# Verificar que escucha en localhost:8000
curl http://127.0.0.1:8000

# Verificar configuración de Nginx
sudo nginx -t
```

### Error de permisos

```bash
# Asegurar permisos correctos
sudo chown -R ubuntu:ubuntu /home/ubuntu/fs2Project
sudo chmod +x deploy.sh setup-nginx.sh
```

### Base de datos no conecta

```bash
# Verificar que el contenedor db está corriendo
docker compose -f docker-compose.prod.yml ps db

# Ver logs
docker compose -f docker-compose.prod.yml logs db

# Verificar variables de entorno
docker compose -f docker-compose.prod.yml exec web env | grep POSTGRES
```

## 📊 Monitoreo

### Health Check

```bash
curl http://app.linusmartinez.com/health
```

### Recursos del Sistema

```bash
docker stats
df -h
free -h
```

## 🔄 Actualización

Para actualizar la aplicación:

1. **Automático**: Haz push a `main` o `master`
2. **Manual**: Ejecuta `./deploy.sh`

El proceso:
- Actualiza el código
- Reconstruye las imágenes
- Reinicia los contenedores
- Ejecuta migraciones
- Recopila estáticos

## 📝 Notas

- Los archivos estáticos se recopilan en `src/staticfiles/` y se sirven por Nginx
- Los archivos media se guardan en `src/media/` (o en OCI Object Storage si está configurado)
- La base de datos PostgreSQL persiste en un volumen de Docker
- Los logs de Gunicorn se pueden ver con `docker compose logs web`


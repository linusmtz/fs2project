#!/bin/bash
set -e

# Script de deployment manual para la VM
# Uso: ./deploy.sh

echo "🚀 Iniciando deployment..."

# Variables
APP_DIR="/home/ubuntu/fs2Project"
REPO_URL="${REPO_URL:-https://github.com/tu-usuario/fs2Project.git}"

# Crear directorio si no existe
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# Clonar o actualizar repositorio
if [ -d ".git" ]; then
  echo "📥 Actualizando repositorio..."
  git fetch origin
  git reset --hard origin/main || git reset --hard origin/master
else
  echo "📥 Clonando repositorio..."
  git clone "$REPO_URL" .
fi

# Verificar que existe .env
if [ ! -f "src/.env" ]; then
  echo "❌ ERROR: src/.env no existe."
  echo "Por favor crea el archivo src/.env con las siguientes variables:"
  echo "  - SECRET_KEY"
  echo "  - DEBUG=0"
  echo "  - ALLOWED_HOSTS=app.linusmartinez.com"
  echo "  - CSRF_TRUSTED_ORIGINS=http://app.linusmartinez.com"
  echo "  - POSTGRES_DB"
  echo "  - POSTGRES_USER"
  echo "  - POSTGRES_PASSWORD"
  echo "  - Y las demás variables necesarias"
  exit 1
fi

# Construir y levantar contenedores
echo "🔨 Construyendo contenedores..."
docker compose -f docker-compose.prod.yml build --no-cache

echo "🚀 Levantando contenedores..."
docker compose -f docker-compose.prod.yml up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 15

# Ejecutar migraciones
echo "📊 Ejecutando migraciones..."
docker compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "📦 Recopilando archivos estáticos..."
docker compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Verificar que los contenedores estén corriendo
echo "✅ Verificando contenedores..."
docker compose -f docker-compose.prod.yml ps

# Limpiar imágenes antiguas
echo "🧹 Limpiando imágenes antiguas..."
docker image prune -f

echo "✅ Deployment completado exitosamente!"
echo "🌐 La aplicación debería estar disponible en http://app.linusmartinez.com"


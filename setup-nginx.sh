#!/bin/bash
set -e

# Script para configurar Nginx como reverse proxy
# Ejecutar con: sudo ./setup-nginx.sh

echo "🔧 Configurando Nginx..."

NGINX_CONFIG="/etc/nginx/sites-available/app.linusmartinez.com"
NGINX_ENABLED="/etc/nginx/sites-enabled/app.linusmartinez.com"
APP_DIR="/home/ubuntu/fs2Project"

# Verificar que Nginx está instalado
if ! command -v nginx &> /dev/null; then
    echo "❌ Nginx no está instalado. Instalando..."
    sudo apt update
    sudo apt install -y nginx
fi

# Crear directorio para archivos estáticos
sudo mkdir -p "$APP_DIR/src/staticfiles"
sudo mkdir -p "$APP_DIR/src/media"
sudo chown -R ubuntu:ubuntu "$APP_DIR"

# Crear configuración de Nginx
echo "📝 Creando configuración de Nginx..."
sudo tee "$NGINX_CONFIG" > /dev/null <<EOF
server {
    listen 80;
    server_name app.linusmartinez.com 129.80.212.133 _;

    # Tamaño máximo de archivos subidos
    client_max_body_size 100M;

    # Archivos estáticos (servidos por Nginx para mejor rendimiento)
    location /static/ {
        alias $APP_DIR/src/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Archivos media (si no usas cloud storage)
    location /media/ {
        alias $APP_DIR/src/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Proxy a Gunicorn en Docker
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
}
EOF

# Habilitar el sitio
if [ ! -L "$NGINX_ENABLED" ]; then
    echo "🔗 Habilitando sitio..."
    sudo ln -s "$NGINX_CONFIG" "$NGINX_ENABLED"
fi

# Verificar configuración
echo "✅ Verificando configuración de Nginx..."
sudo nginx -t

# Recargar Nginx
echo "🔄 Recargando Nginx..."
sudo systemctl reload nginx

echo "✅ Nginx configurado exitosamente!"
echo "🌐 La aplicación debería estar disponible en http://app.linusmartinez.com"


FROM python:3.13-slim

WORKDIR /app

# Instalar dependências do sistema (incluindo curl para health check)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 5000

# NOTE: Removed HEALTHCHECK - Railway uses native health checking with dynamic PORT variable
# Docker HEALTHCHECK cannot interpolate env vars, so hardcoded port conflicts with Railway's PORT injection
# Railway will automatically health check the service via its own mechanisms

# Comando de inicialização (Railway injeta PORT como env var)
CMD ["sh", "-c", "exec gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} --timeout 120 --graceful-timeout 30 --access-logfile - --error-logfile - src.webhook.app:app"]

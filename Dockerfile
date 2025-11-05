FROM python:3.13-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 5000

# Health check (usa PORT dinâmica do Railway)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:${PORT:-5000}/health || exit 1

# Comando de inicialização
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:${PORT:-5000}", "--timeout", "120", "--graceful-timeout", "30", "src.webhook.app:app"]

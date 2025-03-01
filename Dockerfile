FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    wget \
    gnupg \
    git \
    curl \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxcb1 \
    libxkbcommon0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    fonts-liberation \
    libappindicator3-1 \
    libxtst6 \
    xdg-utils \
    xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt .

# Atualizar pip e instalar dependências com retry
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt || \
    (echo "Primeiro tentativa falhou, tentando novamente..." && \
    pip install --no-cache-dir -r requirements.txt)

# Copiar o script de inicialização e torná-lo executável
COPY startup.sh .
RUN chmod +x startup.sh

# Copiar o restante do código do aplicativo
COPY . .

# Instalar navegadores para Playwright de forma não interativa
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN playwright install --with-deps chromium

# Expor a porta que o Streamlit usará
ENV PORT=8501
EXPOSE 8501
EXPOSE 8000

# Variáveis de ambiente adicionais
ENV PYTHONUNBUFFERED=1

# Comando para iniciar o aplicativo
CMD ["./startup.sh"]
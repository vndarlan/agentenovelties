FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema necessárias para o Playwright e SQLAlchemy com PostgreSQL
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    wget \
    gnupg \
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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt .

# Atualizar pip e instalar dependências
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Instalar navegadores para Playwright
RUN playwright install --with-deps chromium

# Copiar o restante do código do aplicativo
COPY . .

# Expor a porta que o Streamlit usará
ENV PORT=8501
EXPOSE 8501

# Comando para iniciar o aplicativo
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
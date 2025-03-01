FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    wget \
    curl \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Atualizar pip e instalar dependências básicas
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copiar apenas o requirements.txt primeiro
COPY requirements.txt .

# Instalar dependências em etapas para melhor diagnóstico
RUN echo "Instalando streamlit e pandas..." && \
    pip install --no-cache-dir streamlit==1.42.0 pandas==1.5.3 && \
    echo "Instalando SQLAlchemy..." && \
    pip install --no-cache-dir SQLAlchemy==2.0.15 sqlalchemy-utils==0.40.0 && \
    echo "Instalando psycopg2..." && \
    pip install --no-cache-dir psycopg2-binary==2.9.6 && \
    echo "Instalando outras dependências..." && \
    pip install --no-cache-dir pydantic==1.10.8 python-dotenv==1.0.0 Pillow==9.5.0 && \
    echo "Instalando playwright..." && \
    pip install --no-cache-dir playwright==1.38.0

# Instalar navegadores para Playwright (com tratamento de erros)
RUN echo "Instalando navegadores Playwright..." && \
    playwright install --with-deps chromium || echo "Falha na primeira tentativa, tentando novamente..." && \
    playwright install --with-deps chromium || echo "Aviso: problemas ao instalar navegadores Playwright."

# Copiar o restante do código do aplicativo
COPY . .

# Expor a porta que o Streamlit usará
ENV PORT=8501
EXPOSE 8501

# Variáveis de ambiente adicionais
ENV PYTHONUNBUFFERED=1

# Criar diretório para healthcheck
RUN mkdir -p /app/_stcore

# Comando para iniciar o aplicativo
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema mínimas
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    wget \
    gnupg \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt .

# Atualizar pip e instalar dependências
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código do aplicativo
COPY . .

# Instalar navegadores para Playwright (com retry para maior robustez)
RUN pip install playwright && \
    playwright install --with-deps chromium || \
    playwright install --with-deps chromium

# Expor a porta que o Streamlit usará
ENV PORT=8501
EXPOSE 8501

# Comando para iniciar o aplicativo
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    wget \
    curl \
    gnupg \
    git \
    # Dependências para o Playwright
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libxcursor1 \
    libgtk-3-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Atualizar pip
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install playwright==1.38.0

# Instalar Playwright e navegadores
RUN python -m playwright install --with-deps chromium || \
    echo "Aviso: Instalação do Playwright pode estar incompleta, mas continuando..."

# Copiar o código da aplicação
COPY . .

# Assegurar que os arquivos Python de instalação e fallback estejam presentes
COPY install_browser_use.py install_langchain.py ./

# Pré-executar o script de fallback para garantir que tudo está configurado
RUN python install_browser_use.py && \
    python install_langchain.py

# Renomear o app minimalista para ser executado corretamente
RUN cp minimal_app.py app.py || echo "Arquivo minimal_app.py não encontrado, usando app.py atual"

# Expor a porta
ENV PORT=8501
EXPOSE 8501

# Configurações adicionais
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Comando para iniciar o aplicativo
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
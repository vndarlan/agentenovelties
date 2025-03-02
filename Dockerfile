FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema necessárias com melhor tratamento de erros
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpq-dev \
    wget \
    curl \
    gnupg \
    lsb-release \
    ca-certificates \
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
    fonts-noto-color-emoji \
    fonts-freefont-ttf \
    libgconf-2-4 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && echo "Instalação de dependências do sistema concluída"

# Atualizar pip e instalar dependências básicas
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copiar apenas o requirements.txt primeiro
COPY requirements.txt .

# Instalar dependências Python com melhor diagnóstico
RUN pip install --no-cache-dir -r requirements.txt && \
    echo "Instalação de dependências Python concluída"

# Verificar módulos instalados para diagnóstico
RUN pip list

# Instalar navegadores para Playwright com melhor diagnóstico
RUN echo "Instalando navegadores Playwright..." && \
    python -m playwright install --with-deps chromium && \
    echo "Instalação do Playwright concluída"

# Verificar se o Playwright foi instalado corretamente
RUN ls -la /ms-playwright || echo "Diretório ms-playwright não encontrado"

# Copiar o restante do código do aplicativo
COPY . .

# Verificar arquivos copiados para diagnóstico
RUN ls -la

# Garantir que os scripts estejam executáveis
RUN chmod +x startup.sh

# Expor a porta que o Streamlit usará
ENV PORT=8501
EXPOSE 8501

# Variáveis de ambiente adicionais
ENV PYTHONUNBUFFERED=1

# Criar diretório para healthcheck
RUN mkdir -p /app/_stcore

# Comando para iniciar o aplicativo (com redirecionamento de logs)
CMD bash startup.sh 2>&1 | tee /app/startup.log
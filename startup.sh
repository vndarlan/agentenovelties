#!/bin/bash
set -e

echo "🔄 Iniciando script de inicialização..."

# Verificar se o Playwright já está instalado
if [ -d "/ms-playwright" ]; then
  echo "✅ Playwright já instalado em /ms-playwright"
else
  echo "🔄 Instalando Playwright..."
  playwright install --with-deps chromium
  echo "✅ Playwright instalado com sucesso"
fi

# Iniciar o Streamlit
echo "🚀 Iniciando Streamlit..."
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
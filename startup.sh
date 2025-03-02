#!/bin/bash
# Script de inicialização atualizado com melhor diagnóstico e tratamento de erros

set +e  # Não sair em caso de erro

echo "🔄 Iniciando script de inicialização..."
echo "📋 Diretório atual: $(pwd)"
echo "📋 Listando arquivos: $(ls -la)"
echo "📋 Variáveis de ambiente: PORT=$PORT, RAILWAY_ENVIRONMENT=$RAILWAY_ENVIRONMENT"

# Função para verificar se um arquivo existe
check_file() {
    if [ -f "$1" ]; then
        echo "✅ Arquivo $1 encontrado"
    else
        echo "❌ Arquivo $1 não encontrado"
    fi
}

# Verificar arquivos críticos
check_file "app.py"
check_file "minimal_app.py"
check_file "install_browser_use.py"
check_file "install_langchain.py"
check_file "requirements.txt"

# Iniciar servidor de healthcheck em segundo plano na porta 8000
echo "🔄 Iniciando servidor de healthcheck na porta 8000..."
python -c "
import http.server
import socketserver

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        return

with socketserver.TCPServer(('0.0.0.0', 8000), HealthHandler) as httpd:
    print('Servidor healthcheck rodando na porta 8000')
    httpd.serve_forever()
" &

# Verificar se o Playwright já está instalado
if [ -d "/ms-playwright" ] && [ -d "/ms-playwright/chromium" ]; then
    echo "✅ Playwright já instalado em /ms-playwright"
    echo "📋 Conteúdo do diretório Playwright: $(ls -la /ms-playwright)"
else
    echo "🔄 Instalando Playwright..."
    python -m playwright install --with-deps chromium || echo "⚠️ Falha ao instalar Playwright, mas continuando..."
fi

# Configurar os módulos de fallback
echo "🔄 Configurando módulos de fallback..."
python install_browser_use.py || echo "⚠️ Falha na configuração do fallback de browser-use, mas continuando..."
python install_langchain.py || echo "⚠️ Falha na configuração do fallback de langchain, mas continuando..."

# Determinar qual app iniciar
if [ -f "minimal_app.py" ]; then
    echo "🔄 Usando minimal_app.py como aplicativo principal"
    APP_TO_RUN="minimal_app.py"
    # Copiar para app.py para compatibilidade
    cp minimal_app.py app.py
else
    echo "🔄 Usando app.py como aplicativo principal"
    APP_TO_RUN="app.py"
fi

# Verificar conexão com o banco de dados
echo "🔄 Verificando conexão com o banco de dados..."
python -c "
import os
import time
import psycopg2

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

if not DATABASE_URL:
    print('Nenhum DATABASE_URL encontrado, usando SQLite')
    exit(0)

# Tentar conectar ao banco de dados com retry
for i in range(5):
    try:
        print(f'Tentativa {i+1} de conectar ao banco de dados...')
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=30)
        conn.close()
        print('Conexão com o banco de dados bem-sucedida!')
        break
    except Exception as e:
        print(f'Erro ao conectar ao banco de dados: {e}')
        if i < 4:
            print(f'Aguardando antes de tentar novamente...')
            time.sleep(5)
"

# Iniciar o Streamlit
echo "🚀 Iniciando Streamlit com aplicativo: $APP_TO_RUN"
streamlit run $APP_TO_RUN --server.port=$PORT --server.address=0.0.0.0 --logger.level=debug
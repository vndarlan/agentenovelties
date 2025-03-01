#!/bin/bash
# Não usar set -e para evitar saída prematura
set +e

echo "🔄 Iniciando script de inicialização..."

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
    print('Servidor rodando na porta 8000')
    httpd.serve_forever()
" &

# Verificar se o Playwright já está instalado
if [ -d "/ms-playwright" ] && [ -d "/ms-playwright/chromium" ]; then
  echo "✅ Playwright já instalado em /ms-playwright"
else
  echo "🔄 Instalando Playwright..."
  # Tentar até 3 vezes instalar o Playwright
  for i in {1..3}; do
    playwright install --with-deps chromium && break || echo "Tentativa $i falhou"
    sleep 5
  done
  echo "✅ Playwright instalado com sucesso"
fi

# Aguardar um pouco para garantir que tudo esteja pronto
sleep 3

# Verifica se o banco de dados está acessível
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
echo "🚀 Iniciando Streamlit..."
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
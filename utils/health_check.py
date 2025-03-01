import streamlit as st
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

def run_healthcheck_server():
    """
    Inicia um servidor HTTP simples para responder a healthchecks do Railway
    em uma porta separada enquanto o Streamlit estiver inicializando
    """
    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            
        def log_message(self, format, *args):
            # Desabilitar logs
            return
    
    # Usar porta 8000 para o healthcheck temporário
    port = int(os.environ.get('HEALTH_PORT', 8000))
    
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    
    print(f"Iniciando servidor de healthcheck na porta {port}")
    
    # Executar o servidor por 2 minutos (tempo suficiente para o Streamlit iniciar)
    # e então encerrar automaticamente
    server.timeout = 120
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # Aguardar 2 minutos e encerrar o servidor
    time.sleep(120)
    server.shutdown()
    print("Servidor de healthcheck encerrado")

def setup_health_check():
    """Configura o healthcheck para ambientes de produção"""
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_PUBLIC_DOMAIN'):
        thread = threading.Thread(target=run_healthcheck_server)
        thread.daemon = True
        thread.start()
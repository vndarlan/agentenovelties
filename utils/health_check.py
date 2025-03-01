import streamlit as st
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import time

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
        
    def log_message(self, format, *args):
        # Desabilitar logs
        return

def run_healthcheck_server():
    """
    Inicia um servidor HTTP simples para responder a healthchecks
    e mantém ele ativo durante toda a execução da aplicação
    """
    try:
        # Usar porta 8000 para o healthcheck
        port = int(os.environ.get('HEALTH_PORT', 8000))
        
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        
        print(f"Iniciando servidor de healthcheck na porta {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Erro ao iniciar servidor de healthcheck: {e}")

def setup_health_check():
    """Configura o healthcheck para ambientes de produção"""
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_PUBLIC_DOMAIN'):
        print("Ambiente Railway detectado, iniciando servidor de healthcheck...")
        # Criar uma thread daemon que continuará rodando em segundo plano
        thread = threading.Thread(target=run_healthcheck_server)
        thread.daemon = True
        thread.start()
        print("Servidor de healthcheck iniciado em thread separada")
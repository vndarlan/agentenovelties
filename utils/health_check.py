import os
import http.server
import socketserver
import threading

def start_healthcheck_server():
    """Inicia um servidor HTTP simples para healthchecks"""
    class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        
        def log_message(self, format, *args):
            return  # Silenciar logs
    
    # Usar porta 8000 para o healthcheck
    port = int(os.environ.get('HEALTH_PORT', 8000))
    
    try:
        httpd = socketserver.TCPServer(('', port), HealthCheckHandler)
        print(f"Iniciando servidor healthcheck na porta {port}")
        httpd.serve_forever()
    except Exception as e:
        print(f"Erro ao iniciar servidor healthcheck: {e}")

def setup_healthcheck():
    """Configura o healthcheck em uma thread separada"""
    thread = threading.Thread(target=start_healthcheck_server)
    thread.daemon = True
    thread.start()
    print("Servidor healthcheck iniciado em thread separada")
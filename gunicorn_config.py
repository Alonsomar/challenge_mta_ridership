# Configuración para mejor manejo de recursos
bind = "0.0.0.0:8080"
workers = 3  # Número de workers
threads = 2  # Threads por worker
worker_class = 'gthread'  # Usar threads
worker_connections = 1000
timeout = 30
keepalive = 2 

import multiprocessing

chdir = "/app/payement"
wsgi_app = "payement.wsgi:application"
bind = "0.0.0.0:8000"

# Plafonné à 4 workers max en dev, adapte en prod selon les K8s resource limits
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)
worker_class = "gthread"
threads = 2
worker_tmp_dir = "/dev/shm"

timeout = 120
graceful_timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 100

accesslog = "-"
errorlog = "-"
loglevel = "info"